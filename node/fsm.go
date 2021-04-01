package node

import (
	"bufio"
	"compress/gzip"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"

	"github.com/hashicorp/raft"
	"github.com/prologic/bitcask"
)

type fsm Store

func (f *fsm) applyPut(key, val string) interface{} {
	f.mu.Lock()
	defer f.mu.Unlock()
	err := f.kv.Put([]byte(key), []byte(val))
	if err != nil {
		return "ERR:Couldn't put in KV Store\n" + err.Error()
	}
	return "SUCCESS:Put in KV Store"
}

func (f *fsm) applyDelete(key string) interface{} {
	f.mu.Lock()
	defer f.mu.Unlock()
	err := f.kv.Delete([]byte(key))
	if err != nil {
		return "ERR:Couldn't delete\n" + err.Error()
	}
	return "SUCCESS:Deleted"
}

func (f *fsm) applyFlush() interface{} {
	f.mu.Lock()
	defer f.mu.Unlock()
	if err := f.kv.Sync(); err != nil {
		panic(err.Error())
	}
	return nil
}

func (f *fsm) Apply(l *raft.Log) interface{} {
	var c command
	if err := json.Unmarshal(l.Data, &c); err != nil {
		panic(fmt.Sprintf("ERR: Failed to unmarshall command : %s", err.Error()))
	}
	switch c.Op {
	case "put":
		return f.applyPut(c.Key, c.Val)
	case "delete":
		return f.applyDelete(c.Key)
	case "flush":
		return f.applyFlush()
	default:
		panic(fmt.Sprintf("Unknown command %s", c.Op))
	}
}

func (f *fsm) Release() {}

func (f *fsm) Snapshot() (raft.FSMSnapshot, error) {
	return f, nil
}

func (f *fsm) Restore(rc io.ReadCloser) error {
	defer rc.Close()
	f.mu.Lock()
	defer f.mu.Unlock()
	var err error
	if err := f.kv.Close(); err != nil {
		return err
	}
	if err := os.RemoveAll(filepath.Join(f.KVDir, "node.db")); err != nil {
		return err
	}
	f.kv = nil
	f.kv, err = bitcask.Open(f.KVDir)
	if err != nil {
		return err
	}
	num := make([]byte, 8)
	gzr, err := gzip.NewReader(rc)
	if err != nil {
		return err
	}
	r := bufio.NewReader(gzr)
	for {
		if _, err := io.ReadFull(r, num); err != nil {
			if err == io.EOF {
				break
			}
			return err
		}
		key := make([]byte, int(binary.LittleEndian.Uint64(num)))
		if _, err := io.ReadFull(r, key); err != nil {
			return err
		}
		if _, err := io.ReadFull(r, num); err != nil {
			return err
		}
		value := make([]byte, int(binary.LittleEndian.Uint64(num)))
		if _, err := io.ReadFull(r, value); err != nil {
			return err
		}
		if err := f.kv.Put(key, value); err != nil {
			return err
		}
	}
	return gzr.Close()
}

func (f *fsm) Persist(sink raft.SnapshotSink) error {
	f.mu.RLock()
	defer f.mu.RUnlock()
	gzw := gzip.NewWriter(sink)

	err := f.kv.Fold(func(key []byte) error {
		var buf []byte
		value, err := f.kv.Get(key)
		if err != nil {
			return err
		}

		num := make([]byte, 8)
		binary.LittleEndian.PutUint64(num, uint64(len(key)))
		buf = append(buf, num...)
		buf = append(buf, key...)
		binary.LittleEndian.PutUint64(num, uint64(len(value)))
		buf = append(buf, num...)
		buf = append(buf, value...)
		if _, err := gzw.Write(buf); err != nil {
			return err
		}
		return nil
	})
	if err != nil {
		sink.Cancel()
		return err
	}

	err = gzw.Close()
	if err != nil {
		sink.Cancel()
		return err
	}
	sink.Close()
	return nil
}
