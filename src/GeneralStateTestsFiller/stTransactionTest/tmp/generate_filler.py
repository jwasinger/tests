from subprocess import Popen, PIPE, STDOUT
import json, os, sys

FILLER_TEMPLATE_FILE='Opcodes_TransactionInit.json-template'
FILLER_RESULT_FILE='Opcodes_TransactionInitFiller.json'

def compileLLL(source):
  proc = Popen(["lllc", "-x"], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
  data = proc.communicate(input='{0}'.format(source))[0]
  return '0x'+data.strip('\n')

badOps = set([0x0c, 0x0d, 0x0e, 0x0f, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f, 0x3f, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x4b, 0x4c, 0x4d, 0x4e, 0x4f, 0x5c, 0x5d, 0x5e, 0x5f, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xab, 0xac, 0xad, 0xae, 0xaf, 0xb0, 0xb1, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xbb, 0xbc, 0xbd, 0xbe, 0xbf, 0xc0, 0xc1, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xcb, 0xcc, 0xcd, 0xce, 0xcf, 0xd0, 0xd1, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8, 0xd9, 0xda, 0xdb, 0xdc, 0xdd, 0xde, 0xdf, 0xe0, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea, 0xeb, 0xec, 0xed, 0xee, 0xef, 0xf5, 0xf6, 0xf7, 0xf8, 0xf9, 0xfb, 0xfc, 0xfe])

goodOps = { 
  0x00: {
    'name': 'STOP',
    'lll': '{ (STOP) (RETURN 0x0 0x1) }'
  }, 
  0x01: {
    'name': 'ADD',
    'lll': '{ (ADD 0x01 0x01) (RETURN 0x0 0x0) }'
  },
  0x02: {
    'name': 'MUL',
    'lll': '{ (MUL 0x01 0x01) (RETURN 0x0 0x0) }'
  },
  0x03: {
    'name': 'SUB',
    'lll': '{ (SUB 0x01 0x01) (RETURN 0x0 0x0) }'
  },
  0x04: {
    'lll': '{ (DIV 0x01 0x01) (RETURN 0x0 0x0) }',
    'name': 'DIV'
  },
  0x05: {
    'lll': '{ (SDIV 0x01 0x01) (RETURN 0x0 0x0) }',
    'name': 'SDIV'
  },
  0x06: {
    'lll': '{ (MOD 0x01 0x01) (RETURN 0x0 0x0) }',
    'name': 'MOD'
  },
  0x07: {
    'lll': '{ (SMOD 0x01 0x01) (RETURN 0x0 0x0) }',
    'name': 'SMOD'
  },
  0x08: {
    'lll': '{ (ADDMOD 0x01 0x01 0x01) (RETURN 0x0 0x0) }',
    'name': 'ADDMOD'
  },
  0x09: {
    'lll': '{ (MULMOD 0x01 0x01 0x01) (RETURN 0x0 0x0) }',
    'name': 'MULMOD'
  },
  0x0a: {
    'lll': '{ (EXP 0x01 0x01) (RETURN 0x0 0x0) }',
    'name': 'EXP'
  },
  0x0b: {
    'lll': '{ (SIGNEXTEND 0x01 0x01) (RETURN 0x0 0x0) }',
    'name': 'SIGNEXTEND'
  },
  0x10: {
    'lll': '{ (LT 0x01 0x01) (RETURN 0x0 0x0) }',
    'name': 'LT'
  },
  0x11: {
    'lll': '{ (GT 0x01 0x01) (RETURN 0x0 0x0) }',
    'name': 'GT'
  },
  0x12: {
    'lll': '{ (SLT 0x01 0x01) (RETURN 0x0 0x0) }',
    'name': 'SLT'
  },
  0x13: {
    'lll': '{ (SGT 0x01 0x01) (RETURN 0x0 0x0) }',
    'name': 'SGT'
  },
  0x14: {
    'lll': '{ (EQ 0x01 0x01) (RETURN 0x0 0x0) }',
    'name': 'EQ'
  },
  0x15: {
    'name': 'ISZERO',
    'lll': '{ (ISZERO 0x00) (RETURN 0x0 0x0) }'
  },
  0x16: {
    'lll': '{ (AND 0x00 0x00) (RETURN 0x0 0x0) }',
    'name': 'AND'
  },
  0x17: {
    'lll': '{ (OR 0x00 0x00) (RETURN 0x0 0x0) }',
    'name': 'OR'
  },
  0x18: {
    'lll': '{ (XOR 0x00 0x00) (RETURN 0x0 0x0) }',
    'name': 'XOR'
  },
  0x19: {
    'lll': '{ (NOT 0x00) (RETURN 0x0 0x0) }',
    'name': 'NOT'
  },
  0x1a: {
    'name': 'BYTE',
    'lll': '{ (BYTE 0 0x8050201008040201) (RETURN 0x0 0x0) }'
  },
  0x20: {
    'lll': '{ (SHA3 0x00 0x00) (RETURN 0x0 0x0) }',
    'bytecode': '600060002060006000f3',
    'name': 'SHA3'
  },
  0x30: {
    'name': 'ADDRESS',
    'lll': '{ (ADDRESS) (RETURN 0x0 0x0) }'
  },
  0x31: {
    'name': 'BALANCE',
    'lll': '{ (BALANCE 0x0) (RETURN 0x0 0x0) }'
  },
  0x32: {
    'name': 'ORIGIN',
    'lll': '{ (ORIGIN) (RETURN 0x0 0x0) }'
  },
  0x33: {
    'name': 'CALLER',
    'lll': '{ (CALLER) (RETURN 0x0 0x0) }'
  },
  0x34: {
    'name': 'CALLVALUE',
    'lll': '{ (CALLVALUE) (RETURN 0x0 0x0) }'
  },
  0x35: {
    'name': 'CALLDATALOAD',
    'lll': '{ (CALLDATALOAD 0x0) (RETURN 0x0 0x0) }'
  },
  0x36: {
    'name': 'CALLDATASIZE',
    'lll': '{ (CALLDATASIZE) (RETURN 0x0 0x0) }'
  },
  0x37: {
    'name': 'CALLDATACOPY',
    'lll': '{ (CALLDATACOPY 0x0 0x0 0x0) (RETURN 0x0 0x0) }'
  },
  0x38: {
    'name': 'CODESIZE',
    'lll': '{ (CODESIZE) (RETURN 0x0 0x0) }'
  },
  0x39: {
    'name': 'CODECOPY',
    'lll': '{ (CODECOPY 0x1 0x0 (CODESIZE)) [[ 0 ]] (MLOAD 0x1) (RETURN 0x0 0x0) }',
    'expect': """
{{
    "//comment": "CODECOPY: not supported in earlier networks",
    "indexes" : {{
        "data" : {0},
        "gas" : -1,
        "value" : -1
    }},
    "network" : ["Byzantium", "Constantinople"],
    "result" : {{
        "a94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {{
            "nonce" : "1"
        }},
        "6295ee1b4f6dd65047762f924ecd367c17eabf8f": {{
            "nonce": "1",
            "storage": {{
                "0x00": "0x38600060013960015160005560006000f3000000000000000000000000000000"
            }}
        }}
    }}
}},
    """
  },
  0x3a: {
    'name': 'GASPRICE',
    'lll': '{ (GASPRICE) (RETURN 0x0 0x0) }'
  },
  0x3b: {
    'name': 'EXTCODESIZE',
    'lll': '{ (EXTCODESIZE 0x0) (RETURN 0x0 0x0)}'
  },
  0x3c: {
    'name': 'EXTCODECOPY',
    'lll': '{ (EXTCODECOPY 0x1000000000000000000000000000000000000010 0 0 20) (RETURN 0x0 0x0) }'
  },
  0x3d: {
    'name': 'RETURNDATASIZE',
    'lll': '{ (RETURNDATASIZE) (RETURN 0x0 0x0) }',
    'expect': """
{{
    "//comment": "RETURNDATASIZE: not supported in earlier networks",
    "indexes" : {{
        "data" : {0},
        "gas" : -1,
        "value" : -1
    }},
    "network" : ["EIP150", "Homestead", "Frontier"],
    "result" : {{
        "a94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {{
            "nonce" : "1"
        }},
        "6295ee1b4f6dd65047762f924ecd367c17eabf8f": {{
            "shouldnotexist": "1"
        }}
    }}
}},
{{
    "//comment": "RETURNDATASIZE: not supported in earlier networks",
    "indexes" : {{
        "data" : {0},
        "gas" : -1,
        "value" : -1
    }},
    "network" : ["Byzantium", "Constantinople"],
    "result" : {{
        "a94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {{
            "nonce" : "1"
        }},
        "6295ee1b4f6dd65047762f924ecd367c17eabf8f": {{
            "nonce": "1"
        }}
    }}
}},
"""
  },
  0x3e: {
    'name': 'RETURNDATACOPY',
    'lll': '{ (RETURNDATACOPY 0x0 0x0 0x0) (RETURN 0x0 0x0) }',
		'expect': """
{{
    "//comment": "RETURNDATACOPY: not supported in earlier networks",
    "indexes" : {{
        "data" : {0},
        "gas" : -1,
        "value" : -1
    }},
    "network" : ["EIP150", "Homestead", "Frontier"],
    "result" : {{
        "a94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {{
            "nonce" : "1"
        }},
        "6295ee1b4f6dd65047762f924ecd367c17eabf8f": {{
            "shouldnotexist": "1"
        }}
    }}
}},
{{
    "//comment": "RETURNDATACOPY: not supported in earlier networks",
    "indexes" : {{
        "data" : {0},
        "gas" : -1,
        "value" : -1
    }},
    "network" : ["Byzantium", "Constantinople"],
    "result" : {{
        "a94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {{
            "nonce" : "1"
        }},
        "6295ee1b4f6dd65047762f924ecd367c17eabf8f": {{
            "nonce": "1"
        }}
    }}
}},
"""
  },
  0x50: {
    'name': 'POP',
    'lll': '{ 0x00 (POP 0x00) (RETURN 0x0 0x0) }'
  },
  0x51: {
    'name': 'MLOAD',
    'lll': '{ (MLOAD 0x0) (RETURN 0x0 0x0)}'
  },
  0x52: {
    'name': 'MSTORE',
    'lll': '{ (MSTORE 0x00 0x00) (RETURN 0x0 0x0) }'
  },
  0x53: {
    'name': 'MSTORE8',
    'lll': '{ (MSTORE8 0 0xff) (RETURN 0x0 0x0) }'
  },
  0x54: {
    'name': 'SLOAD',
    'lll': '{ (SLOAD 0x0) (RETURN 0x0 0x0) }'
  },
  0x55: {
    'name': 'SSTORE',
    'lll': '{ (SSTORE 0x1 0x1) (RETURN 0x0 0x0) }'
  },
  0x56: {
    'name': 'JUMP',
    'lll': '{ (JUMP 0x4) (STOP) (JUMPDEST) (RETURN 0x0 0x0) }'
  },
  0x57: {
    'name': 'JUMPI',
    'lll': '{ (JUMPI 0x6 0x1) (STOP) (JUMPDEST) (RETURN 0x0 0x0) }'
  },
  0x58: {
    'name': 'PC',
    'lll': '{ (PC) (RETURN 0x0 0x0) }'
  },
  0x59: {
    'name': 'MSIZE',
    'lll': '{ (MSIZE) (RETURN 0x0 0x0) }'
  },
  0x5a: {
    'name': 'GAS',
    'lll': '{ (GAS) (RETURN 0x0 0x0) }'
  },
  0x5b: {
    'name': 'JUMPDEST',
    'lll': '{ (JUMPDEST) (RETURN 0x0 0x0) }'
  },
  0x60: {
    'name': 'PUSH1',
    'lll': '{ 0xff (RETURN 0x0 0x0)}'
  },
  0x61: {
    'name': 'PUSH2',
    'lll': '{ 0xffff (RETURN 0x0 0x0)}'
  },
  0x62: {
    'name': 'PUSH3',
    'lll': '{ 0xffffff (RETURN 0x0 0x0)}'
  },
  0x63: {
    'name': 'PUSH4',
    'lll': '{ 0xffffffff (RETURN 0x0 0x0)}'
  },
  0x64: {
    'name': 'PUSH5',
    'lll': '{ 0xffffffffff (RETURN 0x0 0x0)}'
  },
  0x65: {
    'name': 'PUSH6',
    'lll': '{ 0xffffffffffff (RETURN 0x0 0x0)}'

  },
  0x66: {
    'name': 'PUSH7',
    'lll': '{ 0xffffffffffffff (return 0x0 0x0)}'
  },
  0x67: {
    'name': 'PUSH8',
    'lll': '{ 0xffffffffffffffff (return 0x0 0x0)}'
  },
  0x68: {
    'name': 'PUSH9',
    'lll': '{ 0xffffffffffffffffff (return 0x0 0x0)}'

  },
  0x69: {
    'name': 'PUSH10',
    'lll': '{ 0xffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x6a: {
    'name': 'PUSH11',
    'lll': '{ 0xffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x6b: {
    'name': 'PUSH12',
    'lll': '{ 0xffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x6c: {
    'name': 'PUSH13',
    'lll': '{ 0xffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x6d: {
    'name': 'PUSH14',
    'lll': '{ 0xffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x6e: {
    'name': 'PUSH15',
    'lll': '{ 0xffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x6f: {
    'name': 'PUSH16',
    'lll': '{ 0xffffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x70: {
    'name': 'PUSH17',
    'lll': '{ 0xffffffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x71: {
    'name': 'PUSH18',
    'lll': '{ 0xffffffffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x72: {
    'name': 'PUSH19',
    'lll': '{ 0xffffffffffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x73: {
    'name': 'PUSH20',
    'lll': '{ 0xffffffffffffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x74: {
    'name': 'PUSH21',
    'lll': '{ 0xffffffffffffffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x75: {
    'name': 'PUSH22',
    'lll': '{ 0xffffffffffffffffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x76: {
    'name': 'PUSH23',
    'lll': '{ 0xffffffffffffffffffffffffffffffffffffffffffffff (return 0x0 0x0)}'

  },
  0x77: {
    'name': 'PUSH24',
    'lll': '{ 0xffffffffffffffffffffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x78: {
    'name': 'PUSH25',
    'lll': '{ 0xffffffffffffffffffffffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x79: {
    'name' : 'PUSH26',
    'lll': '{ 0xffffffffffffffffffffffffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x7a: {
    'name': 'PUSH27',
    'lll': '{ 0xffffffffffffffffffffffffffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x7b: {
    'name': 'PUSH28',
    'lll': '{ 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x7c: {
    'name': 'PUSH29',
    'lll': '{ 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x7d: {
    'name': 'PUSH30',
    'lll': '{ 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x7e: {
    'name': 'PUSH31',
    'lll': '{ 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x7f: {
    'name': 'PUSH32',
    'lll': '{ 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff (return 0x0 0x0)}'
  },
  0x80: {
    'name': 'DUP1',
    'lll': '{ (DUP1 0xff) (return 0x0 0x0)}'
  },
  0x81: {
    'name': 'DUP2',
    'lll': '{ (DUP2 0xff 0xff) (return 0x0 0x0)}'

  },
  0x82: {
    'name': 'DUP3',
    'lll': '{ (DUP3 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x83: {
    'name': 'DUP4',
    'lll': '{ (DUP4 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x84: {
    'name': 'DUP5',
    'lll': '{ (DUP5 0xff 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x85: {
    'name': 'DUP6',
    'lll': '{ (DUP6 0xff 0xff 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x86: {
    'name': 'DUP7',
    'lll': '{ (DUP7 0xff 0xff 0xff 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x87: {
    'name': 'DUP8',
    'lll': '{ (DUP8 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x88: {
    'name': 'DUP9',
    'lll': '{ (DUP9 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'

  },
  0x89: {
    'name': 'DUP10',
    'lll': '{ (DUP10 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x8a: {
    'name': 'DUP11',
    'lll': '{ (DUP11 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'

  },
  0x8b: {
    'name': 'DUP12',
    'lll': '{ (dup12 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x8c: {
    'name': 'DUP13',
    'lll': '{ (dup13 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x8d: {
    'name': 'DUP14',
    'lll': '{ (dup14 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x8e: {
    'name': 'DUP15',
    'lll': '{ (dup15 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x8f: {
    'name': 'DUP16',
    'lll': '{ (dup16 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x90: {
    'name': 'SWAP1',
    'lll': '{ (SWAP1 0xff 0xff) (return 0x0 0x0)}'
  },
  0x91: {
    'name': 'SWAP2',
    'lll': '{ (swap2 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x92: {
    'name': 'SWAP3',
    'lll': '{ (swap3 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x93: {
    'name': 'SWAP4',
    'lll': '{ (swap4 0xff 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x94: {
    'name': 'SWAP5',
    'lll': '{ (swap5 0xff 0xff 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x95: {
    'name': 'SWAP6',
    'lll': '{ (swap6 0xff 0xff 0xff 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x96: {
    'name': 'SWAP7',
    'lll': '{ (swap7 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff) (return 0x0 0x0)}'
  },
  0x97: {
    'name': 'SWAP8',
    'lll': '{ (swap8 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0x00) (return 0x0 0x0)}'
  },
  0x98: {
    'name' : 'SWAP9',
    'lll': '{ (swap9 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0x00) (return 0x0 0x0)}'
  },
  0x99: {
    'name': 'SWAP10',
    'lll': '{ (swap10 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0x00) (return 0x0 0x0)}'
  },
  0x9a: {
    'name': 'SWAP11',
    'lll': '{ (swap11 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0x00) (return 0x0 0x0)}'
  },
  0x9b: {
    'name': 'SWAP12',
    'lll': '{ (swap12 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0x00) (return 0x0 0x0)}'
  },
  0x9c: {
    'name': 'SWAP13',
    'lll': '{ (swap13 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0x00) (return 0x0 0x0)}'
  },
  0x9d: {
    'name': 'SWAP14',
    'lll': '{ (swap14 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0x00) (return 0x0 0x0)}'
  },
  0x9e: {
    'name': 'SWAP15',
    'lll': '{ (swap15 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0x00) (return 0x0 0x0)}'
  },
  0x9f: {
    'name': 'SWAP16',
    'lll': '{ (swap16 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0xff 0x00) (return 0x0 0x0)}'
  },
  0xa0: {
    'name': 'LOG0',
    'lll': '{ (LOG0 0 0) (return 0x0 0x0) }'
  },
  0xa1: {
    'name': 'LOG1',
    'lll': '{ (LOG1 0 0 0xff) (return 0x0 0x0) }'

  },
  0xa2: {
    'name': 'LOG2',
    'lll': '{ (log2 0 0 0xff 0xff) (return 0x0 0x0) }'
  },
  0xa3: {
    'name': 'LOG3',
    'lll': '{ (log3 0 0 0xff 0xff 0xff) (return 0x0 0x0) }'
  },
  0xa4: {
    'name': 'LOG4',
    'lll': '{ (log4 0 0 0xff 0xff 0xff 0xff) (return 0x0 0x0) }'
  },
  0xf0: {
    'name': 'CREATE',
    'lll': '{ (CREATE 0xff 0x0 0x0) (return 0x0 0x0) }',
		'expect': """
{{   
    "indexes" : {{ 
        "data" : {0}, 
        "gas" : -1, 
        "value" : -1
    }},  
    "network" : ["EIP158", "Byzantium", "Constantinople"],
    "result" : {{ 
        "a94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {{ 
            "nonce" : "1" 
        }},  
        "6295ee1b4f6dd65047762f924ecd367c17eabf8f": {{ 
            "nonce": "2"
        }} 
    }}   
}},
{{   
    "indexes" : {{ 
        "data" : {0}, 
        "gas" : -1, 
        "value" : -1
    }},  
    "network" : ["Frontier", "Homestead", "EIP150"],
    "result" : {{ 
        "a94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {{ 
            "nonce" : "1" 
        }},  
        "6295ee1b4f6dd65047762f924ecd367c17eabf8f": {{ 
            "nonce": "1"
        }} 
    }}   
}},
"""
  },
  0xf1: {
    'name': 'CALL',
    'lll': '{ (call 100 0x0f572e5295c57f15886f9b263e2f6d2d6c7b5ec6 23 0 0 0 0) (return 0x0 0x0) }'
  },
  0xf2: {
    'name': 'CALLCODE',
    'lll': '{ (CALLCODE 100 0x0f572e5295c57f15886f9b263e2f6d2d6c7b5ec6 0 0 0 0 0) (return 0x0 0x0) }'
  },
  0xf3: {
    'name': 'RETURN',
    'lll': '{ (RETURN 0x0 0x0) }'
  },
  0xf4: {
    'name': 'DELEGATECALL',
    'lll': '{ (DELEGATECALL 100000 0x0f572e5295c57f15886f9b263e2f6d2d6c7b5ec6 0 0 0 0) (return 0x0 0x0) }',
		'expect': """
{{   
    "indexes" : {{ 
        "data" : {0}, 
        "gas" : -1, 
        "value" : -1
    }},  
    "network" : ["Homestead", "EIP150", "EIP158", "Byzantium", "Constantinople"],
    "result" : {{ 
        "a94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {{ 
            "nonce" : "1" 
        }},  
        "6295ee1b4f6dd65047762f924ecd367c17eabf8f": {{ 
            "nonce": "1"
        }} 
    }}   
}},
{{   
    "indexes" : {{ 
        "data" : {0}, 
        "gas" : -1, 
        "value" : -1
    }},  
    "network" : ["Frontier"],
    "result" : {{ 
        "a94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {{ 
            "nonce" : "1" 
        }},  
        "6295ee1b4f6dd65047762f924ecd367c17eabf8f": {{ 
            "shouldnotexist": "1"
        }} 
    }}   
}},
"""
  },
  0xfa: {
    'name': 'STATICCALL',
    'lll': '{ (STATICCALL 10000 0x0f572e5295c57f15886f9b263e2f6d2d6c7b5ec6 0 0 0 0) (return 0x0 0x0) }',
		'expect': """
{{   
    "indexes" : {{ 
        "data" : {0}, 
        "gas" : -1, 
        "value" : -1
    }},  
    "network" : ["Byzantium", "Constantinople"],
    "result" : {{ 
        "a94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {{ 
            "nonce" : "1" 
        }},  
        "6295ee1b4f6dd65047762f924ecd367c17eabf8f": {{ 
            "nonce": "1"
        }} 
    }}   
}},
{{   
    "indexes" : {{ 
        "data" : {0}, 
        "gas" : -1, 
        "value" : -1
    }},  
    "network" : ["Frontier", "Homestead", "EIP150", "EIP158"],
    "result" : {{ 
        "a94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {{ 
            "nonce" : "1" 
        }},  
        "6295ee1b4f6dd65047762f924ecd367c17eabf8f": {{ 
            "shouldnotexist": "1"
        }} 
    }}   
}},
"""
  },
  0xfd: {
    'name': 'REVERT',
    'lll': '{ (REVERT 0x0 0x0) (return 0x0 0x0)}',
    'expect': """
{{
    "indexes" : {{ 
        "data" : {0}, 
        "gas" : -1, 
        "value" : -1
    }},
    "network" : ["ALL"],
    "result" : {{
        "a94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {{
            "nonce" : "1"
        }},
        "6295ee1b4f6dd65047762f924ecd367c17eabf8f": {{
            "shouldnotexist": "1"
        }}
    }}
}},
"""
  },
  0xff: {
    'name': 'SELFDESTRUCT',
    'lll': '{ (SELFDESTRUCT (ORIGIN)) }',
		'expect': """
{{
    "indexes" : {{ 
        "data" : {0}, 
        "gas" : -1, 
        "value" : -1
    }},
    "network" : ["EIP158", "Byzantium", "Constantinople"],
    "result" : {{
        "a94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {{
            "nonce" : "1"
        }},
        "6295ee1b4f6dd65047762f924ecd367c17eabf8f": {{
            "shouldnotexist": "1"
        }}
    }}
}},
"""
  }
}

MAX=0x1000000000000000000000

expect_template = """
{{   
    "indexes" : {{ 
        "data" : {0}, 
        "gas" : -1, 
        "value" : -1
    }},  
    "network" : ["Frontier", "Homestead", "EIP150"],
    "result" : {{ 
        "a94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {{ 
            "nonce" : "1" 
        }},  
        "6295ee1b4f6dd65047762f924ecd367c17eabf8f": {{ 
            "nonce": "0"
        }} 
    }}   
}},
{{   
    "indexes" : {{ 
        "data" : {0}, 
        "gas" : -1, 
        "value" : -1
    }},  
    "network" : ["Byzantium", "Constantinople"],
    "result" : {{ 
        "a94f5374fce5edbc8e2a8697c15331677e6ebf0b" : {{ 
            "nonce" : "1" 
        }},  
        "6295ee1b4f6dd65047762f924ecd367c17eabf8f": {{ 
            "nonce": "1"
        }} 
    }}   
}}
"""

def main():
  data = []
  data_with_default_expect = []
  data_with_custom_expect = []
  custom_expects = []

  for index, op in enumerate(goodOps):
    if op > MAX: 
      break
    if index == 52:
      print(op)
    if 'name' in goodOps[op]:
      #print(goodOps[op]['name'])
      if 'bytecode' in goodOps[op]:
        data.append(goodOps[op]['bytecode'])
      elif 'lll' in goodOps[op]:
        data.append(compileLLL(goodOps[op]['lll']))
      
      if 'expect' in goodOps[op]:
        custom_expects.append(goodOps[op]['expect'].format(index))
        data_with_custom_expect.append(index)
      else:
        data_with_default_expect.append(index)

  filler_template = ''
  with open(FILLER_TEMPLATE_FILE, 'r') as f:
    filler_template = f.read()

  import pdb; pdb.set_trace()
  custom_expect = ''.join(custom_expects)
  expect = expect_template.format(json.dumps(data_with_default_expect))
  expect = custom_expect + expect

  s = filler_template.format(expect, json.dumps(data))

  #remove existing filler before overwriting
  try:
    os.remove(FILLER_RESULT_FILE)
  except OSError:
    pass
    
  with open(FILLER_RESULT_FILE, 'w') as f:
    f.write(s)

if __name__ == "__main__":
  main()
