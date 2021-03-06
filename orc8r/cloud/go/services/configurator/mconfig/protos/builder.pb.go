// Code generated by protoc-gen-go. DO NOT EDIT.
// source: builder.proto

package protos

import (
	context "context"
	fmt "fmt"
	proto "github.com/golang/protobuf/proto"
	_ "github.com/golang/protobuf/ptypes/any"
	grpc "google.golang.org/grpc"
	codes "google.golang.org/grpc/codes"
	status "google.golang.org/grpc/status"
	storage "magma/orc8r/cloud/go/services/configurator/storage"
	math "math"
)

// Reference imports to suppress errors if they are not otherwise used.
var _ = proto.Marshal
var _ = fmt.Errorf
var _ = math.Inf

// This is a compile-time assertion to ensure that this generated file
// is compatible with the proto package it is being compiled against.
// A compilation error at this line likely means your copy of the
// proto package needs to be updated.
const _ = proto.ProtoPackageIsVersion3 // please upgrade the proto package

type BuildRequest struct {
	// network containing the gateway
	Network *storage.Network `protobuf:"bytes,1,opt,name=network,proto3" json:"network,omitempty"`
	// graph of entities associated with the gateway
	Graph *storage.EntityGraph `protobuf:"bytes,2,opt,name=graph,proto3" json:"graph,omitempty"`
	// gateway_id of the gateway
	GatewayId            string   `protobuf:"bytes,3,opt,name=gateway_id,json=gatewayId,proto3" json:"gateway_id,omitempty"`
	XXX_NoUnkeyedLiteral struct{} `json:"-"`
	XXX_unrecognized     []byte   `json:"-"`
	XXX_sizecache        int32    `json:"-"`
}

func (m *BuildRequest) Reset()         { *m = BuildRequest{} }
func (m *BuildRequest) String() string { return proto.CompactTextString(m) }
func (*BuildRequest) ProtoMessage()    {}
func (*BuildRequest) Descriptor() ([]byte, []int) {
	return fileDescriptor_68a5e6cb4f7c8dc9, []int{0}
}

func (m *BuildRequest) XXX_Unmarshal(b []byte) error {
	return xxx_messageInfo_BuildRequest.Unmarshal(m, b)
}
func (m *BuildRequest) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
	return xxx_messageInfo_BuildRequest.Marshal(b, m, deterministic)
}
func (m *BuildRequest) XXX_Merge(src proto.Message) {
	xxx_messageInfo_BuildRequest.Merge(m, src)
}
func (m *BuildRequest) XXX_Size() int {
	return xxx_messageInfo_BuildRequest.Size(m)
}
func (m *BuildRequest) XXX_DiscardUnknown() {
	xxx_messageInfo_BuildRequest.DiscardUnknown(m)
}

var xxx_messageInfo_BuildRequest proto.InternalMessageInfo

func (m *BuildRequest) GetNetwork() *storage.Network {
	if m != nil {
		return m.Network
	}
	return nil
}

func (m *BuildRequest) GetGraph() *storage.EntityGraph {
	if m != nil {
		return m.Graph
	}
	return nil
}

func (m *BuildRequest) GetGatewayId() string {
	if m != nil {
		return m.GatewayId
	}
	return ""
}

type BuildResponse struct {
	// configs_by_key contains the partial mconfig from this mconfig builder
	// Each config value contains a proto which is
	//  - first serialized to an any.Any proto
	//  - then serialized to JSON
	// TODO(#2310): remove the need to serialize to JSON by sending proto descriptors
	ConfigsByKey         map[string][]byte `protobuf:"bytes,1,rep,name=configs_by_key,json=configsByKey,proto3" json:"configs_by_key,omitempty" protobuf_key:"bytes,1,opt,name=key,proto3" protobuf_val:"bytes,2,opt,name=value,proto3"`
	XXX_NoUnkeyedLiteral struct{}          `json:"-"`
	XXX_unrecognized     []byte            `json:"-"`
	XXX_sizecache        int32             `json:"-"`
}

func (m *BuildResponse) Reset()         { *m = BuildResponse{} }
func (m *BuildResponse) String() string { return proto.CompactTextString(m) }
func (*BuildResponse) ProtoMessage()    {}
func (*BuildResponse) Descriptor() ([]byte, []int) {
	return fileDescriptor_68a5e6cb4f7c8dc9, []int{1}
}

func (m *BuildResponse) XXX_Unmarshal(b []byte) error {
	return xxx_messageInfo_BuildResponse.Unmarshal(m, b)
}
func (m *BuildResponse) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
	return xxx_messageInfo_BuildResponse.Marshal(b, m, deterministic)
}
func (m *BuildResponse) XXX_Merge(src proto.Message) {
	xxx_messageInfo_BuildResponse.Merge(m, src)
}
func (m *BuildResponse) XXX_Size() int {
	return xxx_messageInfo_BuildResponse.Size(m)
}
func (m *BuildResponse) XXX_DiscardUnknown() {
	xxx_messageInfo_BuildResponse.DiscardUnknown(m)
}

var xxx_messageInfo_BuildResponse proto.InternalMessageInfo

func (m *BuildResponse) GetConfigsByKey() map[string][]byte {
	if m != nil {
		return m.ConfigsByKey
	}
	return nil
}

func init() {
	proto.RegisterType((*BuildRequest)(nil), "magma.orc8r.configurator.mconfig.BuildRequest")
	proto.RegisterType((*BuildResponse)(nil), "magma.orc8r.configurator.mconfig.BuildResponse")
	proto.RegisterMapType((map[string][]byte)(nil), "magma.orc8r.configurator.mconfig.BuildResponse.ConfigsByKeyEntry")
}

func init() { proto.RegisterFile("builder.proto", fileDescriptor_68a5e6cb4f7c8dc9) }

var fileDescriptor_68a5e6cb4f7c8dc9 = []byte{
	// 348 bytes of a gzipped FileDescriptorProto
	0x1f, 0x8b, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0xff, 0x94, 0x92, 0xcf, 0x4b, 0xc3, 0x30,
	0x14, 0xc7, 0xcd, 0xc6, 0xd4, 0x65, 0x3f, 0xd0, 0xe0, 0xa1, 0x16, 0x84, 0xb2, 0xd3, 0x3c, 0x98,
	0xc0, 0xbc, 0x0c, 0x2f, 0x6a, 0xc7, 0x10, 0x11, 0x3d, 0xf4, 0xe8, 0x65, 0xa4, 0x6d, 0x16, 0xeb,
	0xba, 0x66, 0x26, 0xe9, 0x46, 0xc0, 0xff, 0x4b, 0xfc, 0xef, 0xa4, 0xc9, 0x06, 0x13, 0x91, 0xe9,
	0xe9, 0xfd, 0xe0, 0x7d, 0x3f, 0xfd, 0xf6, 0xbd, 0xc0, 0x4e, 0x5c, 0x66, 0x79, 0xca, 0x24, 0x5e,
	0x48, 0xa1, 0x05, 0x0a, 0xe6, 0x94, 0xcf, 0x29, 0x16, 0x32, 0x19, 0x4a, 0x9c, 0x88, 0x62, 0x9a,
	0xf1, 0x52, 0x52, 0x2d, 0x24, 0x9e, 0xbb, 0xca, 0x3f, 0xe5, 0x42, 0xf0, 0x9c, 0x11, 0x3b, 0x1f,
	0x97, 0x53, 0x42, 0x0b, 0xe3, 0xc4, 0xfe, 0x8d, 0x15, 0x13, 0x2b, 0x26, 0x49, 0x2e, 0xca, 0x94,
	0x70, 0x41, 0x14, 0x93, 0xcb, 0x2c, 0x61, 0x8a, 0x6c, 0xe3, 0x88, 0xd2, 0x42, 0x52, 0xce, 0x36,
	0xd1, 0x11, 0x7a, 0x1f, 0x00, 0xb6, 0xc3, 0xca, 0x50, 0xc4, 0xde, 0x4a, 0xa6, 0x34, 0x1a, 0xc1,
	0x83, 0x82, 0xe9, 0x95, 0x90, 0x33, 0x0f, 0x04, 0xa0, 0xdf, 0x1a, 0x9c, 0xe3, 0x5f, 0x1d, 0x6e,
	0x50, 0x4f, 0x4e, 0x10, 0x6d, 0x94, 0x68, 0x04, 0x1b, 0x5c, 0xd2, 0xc5, 0x8b, 0x57, 0xb3, 0x88,
	0x8b, 0xdd, 0x88, 0x71, 0xa1, 0x33, 0x6d, 0xee, 0x2a, 0x51, 0xe4, 0xb4, 0xe8, 0x0c, 0x42, 0x4e,
	0x35, 0x5b, 0x51, 0x33, 0xc9, 0x52, 0xaf, 0x1e, 0x80, 0x7e, 0x33, 0x6a, 0xae, 0x3b, 0xf7, 0x69,
	0xef, 0x13, 0xc0, 0xce, 0xda, 0xb9, 0x5a, 0x88, 0x42, 0x31, 0xc4, 0x61, 0xd7, 0xb1, 0xd5, 0x24,
	0x36, 0x93, 0x19, 0x33, 0x1e, 0x08, 0xea, 0xfd, 0xd6, 0xe0, 0x16, 0xef, 0xda, 0x31, 0xfe, 0x06,
	0xc2, 0x23, 0x47, 0x09, 0xcd, 0x03, 0x33, 0xe3, 0x42, 0x4b, 0x13, 0xb5, 0x93, 0xad, 0x96, 0x7f,
	0x0d, 0x8f, 0x7f, 0x8c, 0xa0, 0x23, 0x58, 0x77, 0x9f, 0xac, 0x7c, 0x56, 0x29, 0x3a, 0x81, 0x8d,
	0x25, 0xcd, 0x4b, 0x66, 0xb7, 0xd0, 0x8e, 0x5c, 0x71, 0x55, 0x1b, 0x82, 0xc1, 0x3b, 0xec, 0x3e,
	0x3a, 0x62, 0xe8, 0x1e, 0x03, 0x7a, 0x85, 0x0d, 0x9b, 0x22, 0xfc, 0x67, 0xb3, 0xf6, 0x5e, 0x3e,
	0xf9, 0xe7, 0xcf, 0xf5, 0xf6, 0xc2, 0xc3, 0xe7, 0x7d, 0x7b, 0x7c, 0x15, 0xbb, 0x78, 0xf9, 0x15,
	0x00, 0x00, 0xff, 0xff, 0xee, 0x5e, 0xc1, 0xb6, 0x94, 0x02, 0x00, 0x00,
}

// Reference imports to suppress errors if they are not otherwise used.
var _ context.Context
var _ grpc.ClientConnInterface

// This is a compile-time assertion to ensure that this generated file
// is compatible with the grpc package it is being compiled against.
const _ = grpc.SupportPackageIsVersion6

// MconfigBuilderClient is the client API for MconfigBuilder service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://godoc.org/google.golang.org/grpc#ClientConn.NewStream.
type MconfigBuilderClient interface {
	// Build returns a partial mconfig containing the gateway configs for which
	// this builder is responsible.
	Build(ctx context.Context, in *BuildRequest, opts ...grpc.CallOption) (*BuildResponse, error)
}

type mconfigBuilderClient struct {
	cc grpc.ClientConnInterface
}

func NewMconfigBuilderClient(cc grpc.ClientConnInterface) MconfigBuilderClient {
	return &mconfigBuilderClient{cc}
}

func (c *mconfigBuilderClient) Build(ctx context.Context, in *BuildRequest, opts ...grpc.CallOption) (*BuildResponse, error) {
	out := new(BuildResponse)
	err := c.cc.Invoke(ctx, "/magma.orc8r.configurator.mconfig.MconfigBuilder/Build", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// MconfigBuilderServer is the server API for MconfigBuilder service.
type MconfigBuilderServer interface {
	// Build returns a partial mconfig containing the gateway configs for which
	// this builder is responsible.
	Build(context.Context, *BuildRequest) (*BuildResponse, error)
}

// UnimplementedMconfigBuilderServer can be embedded to have forward compatible implementations.
type UnimplementedMconfigBuilderServer struct {
}

func (*UnimplementedMconfigBuilderServer) Build(ctx context.Context, req *BuildRequest) (*BuildResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method Build not implemented")
}

func RegisterMconfigBuilderServer(s *grpc.Server, srv MconfigBuilderServer) {
	s.RegisterService(&_MconfigBuilder_serviceDesc, srv)
}

func _MconfigBuilder_Build_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(BuildRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(MconfigBuilderServer).Build(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/magma.orc8r.configurator.mconfig.MconfigBuilder/Build",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(MconfigBuilderServer).Build(ctx, req.(*BuildRequest))
	}
	return interceptor(ctx, in, info, handler)
}

var _MconfigBuilder_serviceDesc = grpc.ServiceDesc{
	ServiceName: "magma.orc8r.configurator.mconfig.MconfigBuilder",
	HandlerType: (*MconfigBuilderServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "Build",
			Handler:    _MconfigBuilder_Build_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "builder.proto",
}
