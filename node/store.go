package node

import (
	"encoding/json"
	"fmt"
	"net"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/hashicorp/raft"
	raftboltdb "github.com/hashicorp/raft-boltdb"
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

func New(storeDir string, clearDir bool) (*Store, string) {
	// Tries to continue from directory if it exists
	if clearDir {
		os.RemoveAll(storeDir)
		os.MkdirAll(storeDir, 0700)
	}
	db, err := bitcask.Open(storeDir)
	if err != nil {
		if clearDir {
			return nil, "ERR:Failed to create KV Store database at given directory\n" + err.Error()
		}
		// If fails removes content in directory and retries
		return New(storeDir, true)
	}
	return &Store{
		kv:    db,
		KVDir: storeDir,
	}, "SUCCESS:Created KV Store"
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
	// os.RemoveAll(s.RaftDir)
	// os.MkdirAll(s.RaftDir, 0700)
	// Snapshots of fsm
	snapshots, err := raft.NewFileSnapshotStore(s.RaftDir, retainSnapshotCount, os.Stderr)
	if err != nil {
		return "ERR:Failed to create snapshot store\n" + err.Error()
	}

	// For Log and Stable storages of raft
	dbStore, err := raftboltdb.NewBoltStore(filepath.Join(s.RaftDir, "raft.db"))
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
	return "SUCCESS:Opened store"
}

func (s *Store) Close() string {
	s.mu.Lock()
	defer s.mu.Unlock()
	err := s.kv.Close()
	if err != nil {
		return "ERR:Couldn't close DB\n" + err.Error()
	}
	return "SUCCESS:Closed DB"
}

func (s *Store) Join(nodeID, addr string) string {
	configFuture := s.raft.GetConfiguration()
	if err := configFuture.Error(); err != nil {
		return "ERR:Failed to get raft configuration" + err.Error()
	}

	for _, srv := range configFuture.Configuration().Servers {
		// If a node already exists with either the joining node's ID or address,
		// that node may need to be removed from the config first.
		if srv.ID == raft.ServerID(nodeID) || srv.Address == raft.ServerAddress(addr) {
			// In case both are same then no need to do anything
			if srv.Address == raft.ServerAddress(addr) && srv.ID == raft.ServerID(nodeID) {
				return "SUCCESS:Node " + nodeID + " at " + addr + " already in raft"
			}

			future := s.raft.RemoveServer(srv.ID, 0, 0)
			if err := future.Error(); err != nil {
				return "ERR:Failed to remove node at " + nodeID + " : " + string(srv.Address) + "\n" + err.Error()
			}
		}
	}

	f := s.raft.AddVoter(raft.ServerID(nodeID), raft.ServerAddress(addr), 0, 0)
	if f.Error() != nil {
		return "ERR:Failed to add as raft voter\n" + f.Error().Error()
	}
	return "SUCCESS:Node " + nodeID + " at " + addr + " joined successfully"
}

func (s *Store) RemoveNode(nodeID string) string {
	future := s.raft.RemoveServer(raft.ServerID(nodeID), 0, 0)
	if err := future.Error(); err != nil {
		return "ERR:Failed to remove node at " + nodeID + "\n" + err.Error()
	}
	return "SUCCESS:Removed Node with ID " + nodeID
}

func (s *Store) Get(key string) string {
	// No need to do apply on FSM as no need to log
	s.mu.RLock()
	defer s.mu.RUnlock()
	fmt.Println("Trying to get ", key)
	fmt.Println("Current kv ", s.kv)
	val, err := s.kv.Get([]byte(key))
	if err != nil {
		return "ERR:Couldn't get value\n" + err.Error()
	}
	return "SUCCESS:" + string(val)
}

func (s *Store) IsLeader() string {
	if s.raft.State() != raft.Leader {
		return "NONLEADER:Not a leader"
	}
	return "SUCCESS:Leader"
}

func (s *Store) Put(key, val string) string {
	if s.raft.State() != raft.Leader {
		return "NONLEADER:Called put on non leader"
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
	if f.Error() != nil {
		return "ERR:Failed Raft Apply" + f.Error().Error()
	}
	return "SUCCESS:Put " + key + " : " + val
}

func (s *Store) Delete(key string) string {
	if s.raft.State() != raft.Leader {
		return "NONLEADER:Called put on non leader"
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
	if f.Error() != nil {
		return "ERR:Failed Raft Apply" + f.Error().Error()
	}
	return "SUCCESS:Delete " + key
}

func (s *Store) Flush() string {
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
