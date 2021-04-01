package ShardedKVStore

import (
	"encoding/json"
	"fmt"
	"net"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/hashicorp/raft"
	raftmdb "github.com/hashicorp/raft-mdb"
	"github.com/prologic/bitcask"
)

type command struct {
	Op  string `json:"op,omitempty"`
	Key string `json:"key,omitempty"`
	Val string `json:"value,omitempty"`
}

type Store struct {
	RaftDir  string
	RaftBind string
	KVDir    string

	mu   sync.RWMutex // Read write lock enables many reads or single write
	kv   *bitcask.Bitcask
	raft *raft.Raft
}

const (
	retainSnapshotCount = 2
	raftTimeout         = 10 * time.Second
)

func New(storeDir string) *Store {
	db, err := bitcask.Open(storeDir)
	if err != nil {
		panic(fmt.Sprintf("ERR:Failed to create KV Store database : %s", err.Error()))
	}
	return &Store{
		kv:    db,
		KVDir: storeDir,
	}
}

func (s *Store) Open(enableSingle bool, serverID string) string {
	config := raft.DefaultConfig()
	config.LocalID = raft.ServerID(serverID)

	addr, err := net.ResolveTCPAddr("tcp", s.RaftBind)
	if err != nil {
		return "ERR:Failed resolving TCP Address\n" + err.Error()
	}
	// Communication of raft machines
	transport, err := raft.NewTCPTransport(s.RaftBind, addr, 3, raftTimeout, os.Stderr)
	if err != nil {
		return "ERR:Failed to create TCP Transport\n" + err.Error()
	}
	// Snapshots of fsm
	snapshots, err := raft.NewFileSnapshotStore(s.RaftDir, retainSnapshotCount, os.Stderr)
	if err != nil {
		return "ERR:Failed to create snapshot store\n" + err.Error()
	}

	// For Log and Stable storages of raft
	dbStore, err := raftmdb.NewMDBStore(filepath.Join(s.RaftDir, "raft.db"))
	if err != nil {
		return "ERR:Failed while initializing MDBStore"
	}
	// Create Raft with fsm and stores
	ra, err := raft.NewRaft(config, (*fsm)(s), dbStore, dbStore, snapshots, transport)
	if err != nil {
		return "ERR:Error initializing raft\n" + err.Error()
	}
	s.raft = ra

	if enableSingle {
		configuration := raft.Configuration{
			Servers: []raft.Server{
				{
					ID:      config.LocalID,
					Address: transport.LocalAddr(),
				},
			},
		}
		ra.BootstrapCluster(configuration)
	}
	return "SUCCESS:Opened new store\n"
}

func (s *Store) Close() string {
	s.mu.Lock()
	defer s.mu.Unlock()
	err := s.kv.Close()
	if err != nil {
		return "ERR:Couldn't close DB\n" + err.Error()
	}
	return "SUCESS:Closed DB"
}

func (s *Store) Get(key string) string {
	// No need to do apply on FSM as no need to log
	s.mu.RLock()
	defer s.mu.RUnlock()
	val, err := s.kv.Get([]byte(key))
	if err != nil {
		return "ERR:Couldn't get value\n" + err.Error()
	}
	return "SUCCESS:" + string(val)
}

func (s *Store) Put(key, val string) string {
	if s.raft.State() != raft.Leader {
		return "ERR:Called put on non leader"
	}
	// Set command to apply on fsm and send it by marshalling into json
	cmd := &command{
		Op:  "put",
		Key: key,
		Val: val,
	}
	body, err := json.Marshal(cmd)
	if err != nil {
		return "ERR:Couldn't marshall command\n" + err.Error()
	}
	f := s.raft.Apply(body, raftTimeout)
	return "ERR:Failed Raft Apply" + f.Error().Error()
}

func (s *Store) Delete(key string) string {
	if s.raft.State() != raft.Leader {
		return "ERR:Called delete on non leader"
	}
	// Set command to apply on fsm and send it by marshalling into json
	cmd := &command{
		Op:  "delete",
		Key: key,
	}
	body, err := json.Marshal(cmd)
	if err != nil {
		return "ERR:Couldn't marshall command\n" + err.Error()
	}
	f := s.raft.Apply(body, raftTimeout)
	return "ERR:Failed Raft Apply" + f.Error().Error()
}

func (s *Store) Flush(key string) string {
	// Set command to apply on fsm and send it by marshalling into json
	cmd := &command{
		Op: "flush",
	}
	body, err := json.Marshal(cmd)
	if err != nil {
		return "ERR:Couldn't marshall command\n" + err.Error()
	}
	f := s.raft.Apply(body, raftTimeout)
	return "ERR:Failed Raft Apply" + f.Error().Error()
}
