/*
Copyright 2020 The Magma Authors.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

// Code generated by mockery v1.0.0. DO NOT EDIT.

package mocks

import blobstore "magma/orc8r/cloud/go/blobstore"
import mock "github.com/stretchr/testify/mock"
import storage "magma/orc8r/cloud/go/storage"

// BlobStorageFactory is an autogenerated mock type for the BlobStorageFactory type
type BlobStorageFactory struct {
	mock.Mock
}

// InitializeFactory provides a mock function with given fields:
func (_m *BlobStorageFactory) InitializeFactory() error {
	ret := _m.Called()

	var r0 error
	if rf, ok := ret.Get(0).(func() error); ok {
		r0 = rf()
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// StartTransaction provides a mock function with given fields: opts
func (_m *BlobStorageFactory) StartTransaction(opts *storage.TxOptions) (blobstore.TransactionalBlobStorage, error) {
	ret := _m.Called(opts)

	var r0 blobstore.TransactionalBlobStorage
	if rf, ok := ret.Get(0).(func(*storage.TxOptions) blobstore.TransactionalBlobStorage); ok {
		r0 = rf(opts)
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(blobstore.TransactionalBlobStorage)
		}
	}

	var r1 error
	if rf, ok := ret.Get(1).(func(*storage.TxOptions) error); ok {
		r1 = rf(opts)
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}
