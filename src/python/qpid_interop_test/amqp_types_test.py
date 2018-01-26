#!/usr/bin/env python

"""
Module to test AMQP primitive types across different clients
"""

#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

import sys
import unittest

from itertools import product
from json import dumps
from time import mktime, time
from uuid import UUID, uuid4

import qpid_interop_test.broker_properties
import qpid_interop_test.qit_common
import qpid_interop_test.shims


class AmqpPrimitiveTypes(qpid_interop_test.qit_common.QitTestTypeMap):
    """
    Class which contains all the described AMQP primitive types and the test values to be used in testing.
    """

    type_map = {
        'null': ['None'],
        'boolean': ['True',
                    'False'],
        'ubyte': ['0x0',
                  '0x7f',
                  '0x80',
                  '0xff'],
        'ushort': ['0x0',
                   '0x7fff',
                   '0x8000',
                   '0xffff'],
        'uint': ['0x0',
                 '0x7fffffff',
                 '0x80000000',
                 '0xffffffff'],
        'ulong': ['0x0',
                  '0x1',
                  '0xff',
                  '0x100',
                  '0x102030405',
                  '0x7fffffffffffffff',
                  '0x8000000000000000',
                  '0xffffffffffffffff'],
        'byte': ['-0x80',
                 '-0x1',
                 '0x0',
                 '0x7f'],
        'short': ['-0x8000',
                  '-0x1',
                  '0x0',
                  '0x7fff'],
        'int': ['-0x80000000',
                '-0x1',
                '0x0',
                '0x7fffffff'],
        'long': ['-0x8000000000000000',
                 '-0x102030405',
                 '-0x81',
                 '-0x80',
                 '-0x1',
                 '0x0',
                 '0x7f',
                 '0x80',
                 '0x102030405',
                 '0x7fffffffffffffff'],
        # float and double: Because of difficulty with rounding of floating point numbers, we use the binary
        # representation instead which should be exact when comparing sent and received values.
        'float': ['0x00000000', # 0.0
                  '0x80000000', # -0.0
                  '0x40490fdb', # pi (3.14159265359) positive decimal
                  '0xc02df854', # -e (-2.71828182846) negative decimal
                  '0x00000001', # Smallest positive denormalized number
                  '0x80000001', # Smallest negative denormalized number
                  '0x007fffff', # Largest positive denormalized number
                  '0x807fffff', # Largest negative denormalized number
                  '0x00800000', # Smallest positive normalized number
                  '0x80800000', # Smallest negative normalized number
                  '0x7f7fffff', # Largest positive normalized number
                  '0xff7fffff', # Largest negative normalized number
                  #'0x7f800000', # +Infinity # PROTON-1149 - fails on RHEL7
                  #'0xff800000', # -Infinity # PROTON-1149 - fails on RHEL7
                  '0x7fc00000', # +NaN
                  #'0xffc00000', # -NaN # Not supported in Javascript
                 ],
        'double': ['0x0000000000000000', # 0.0
                   '0x8000000000000000', # -0.0
                   '0x400921fb54442eea', # pi (3.14159265359) positive decimal
                   '0xc005bf0a8b145fcf', # -e (-2.71828182846) negative decimal
                   '0x0000000000000001', # Smallest positive denormalized number
                   '0x8000000000000001', # Smallest negative denormalized number
                   '0x000fffffffffffff', # Largest positive denormalized number
                   '0x800fffffffffffff', # Largest negative denormalized number
                   '0x0010000000000000', # Smallest positive normalized number
                   '0x8010000000000000', # Smallest negative normalized number
                   '0x7fefffffffffffff', # Largest positive normalized number
                   '0xffefffffffffffff', # Largest negative normalized number
                   '0x7ff0000000000000', # +Infinity
                   '0xfff0000000000000', # -Infinity
                   '0x7ff8000000000000', # +NaN
                   #'0xfff8000000000000', # -NaN # Not supported in Javascript
                  ],
        # decimal32, decimal64, decimal128:
        # Until more formal support for decimal32, decimal64 and decimal128 are included in Python, we use
        # a hex format for basic tests, and treat the data as a binary blob.
        'decimal32': ['0x00000000',
                      '0x40490fdb',
                      '0xc02df854',
                      '0xff7fffff'],
        'decimal64': ['0x0000000000000000',
                      '0x400921fb54442eea',
                      '0xc005bf0a8b145fcf',
                      '0xffefffffffffffff'],
        'decimal128': ['0x00000000000000000000000000000000',
                       '0xff0102030405060708090a0b0c0d0e0f'],
        'char': [u' ', # single ASCII chars
                 u'0',
                 u'A',
                 u'z',
                 u'~',
                 u'0x1', # Hex representation
                 u'0x7f',
                 u'0x16b5', # Rune 'G'
                 u'0x10203',
                 u'0x10ffff',
                 #u'0x12345678' # 32-bit number, not real char # Disabled until Python can handle it
                ],
        # timestamp: Must be in milliseconds since the Unix epoch
        'timestamp': ['0x0',
                      '0x%x' % int(mktime((2000, 1, 1, 0, 0, 0, 5, 1, 0))*1000),
                      '0x%x' % int(time()*1000)
                     ],
        'uuid': [str(UUID(int=0x0)),
                 str(UUID('00010203-0405-0607-0809-0a0b0c0d0e0f')),
                 str(uuid4())],
        'binary': [bytes(),
                   bytes(12345),
                   b'Hello, world',
                   b'\\x01\\x02\\x03\\x04\\x05abcde\\x80\\x81\\xfe\\xff',
                   b'The quick brown fox jumped over the lazy dog 0123456789.' * 100
                  ],
        # strings must be unicode to comply with AMQP spec
        'string': [u'',
                   u'Hello, world',
                   u'"Hello, world"',
                   u"Charlie's peach",
                   u'The quick brown fox jumped over the lazy dog 0123456789.' * 100
                  ],
        'symbol': ['',
                   'myDomain.123',
                   'domain.0123456789.' * 100,
                  ],
        'list': [[],
                 ['ubyte:1', 'int:-2', 'float:3.14'],
                 ['string:a', 'string:b', 'string:c'],
                 ['ulong:12345',
                  'timestamp:%d' % (time()*1000),
                  'short:-2500',
                  'uuid:%s' % uuid4(),
                  'symbol:a.b.c',
                  'none:',
                  'decimal64:0x400921fb54442eea'
                 ],
                 [[],
                  'none',
                  ['ubyte:1', 'ubyte:2', 'ubyte:3'],
                  'boolean:True',
                  'boolean:False',
                  {'string:hello': 'long:1234', 'string:goodbye': 'boolean:True'}
                 ],
                 [[], [[], [[], [], []], []], []],
                 ['short:0',
                  'short:1',
                  'short:2',
                  'short:3',
                  'short:4',
                  'short:5',
                  'short:6',
                  'short:7',
                  'short:8',
                  'short:9'] * 10
                ],
        'map': [{}, # Enpty map
                # Map with string keys
                {'string:one': 'ubyte:1',
                 'string:two': 'ushort:2'},
                # Map with other AMQP simple types as keys
                {'none:': 'string:None',
                 'string:None': 'none:',
                 'string:One': 'long:-1234567890',
                 'short:2': 'int:2',
                 'boolean:True': 'string:True',
                 'string:False': 'boolean:False',
                 #['string:AAA', 'ushort:5951']: 'string:list value',
                 #{'byte:-55': 'ubyte:200',
                 # 'boolean:True': 'string:Hello, world'}: 'symbol:map.value',
                 #'string:list': [],
                 'string:map': {'char:A': 'int:1',
                                'char:B': 'int:2'}},
               ],
        # array: Each array is constructed from the test values in this map. This list contains
        # the keys to the array value types to be included in the test. See function create_test_arrays()
        # for the top-level function that performs the array creation.
        #'array': ['boolean',
        #          'ubyte',
        #          'ushort',
        #          'uint',
        #          'ulong',
        #          'byte',
        #          'short',
        #          'int',
        #          'long',
        #          'float',
        #          'double',
        #          'decimal32',
        #          'decimal64',
        #          'decimal128',
        #          'char',
        #          'uuid',
        #          'binary',
        #          'string',
        #          'symbol',
        #         ],
        }

    # This section contains tests that should be skipped because of known issues that would cause the test to fail.
    # As the issues are resolved, these should be removed.
    broker_skip = {
        'decimal32': {'ActiveMQ': 'decimal32 and decimal64 sent byte reversed: PROTON-1160',
                      'qpid-cpp': 'decimal32 not supported on qpid-cpp broker: QPIDIT-5, QPID-6328',
                      'apache-activemq-artemis': 'decimal32 and decimal64 sent byte reversed: PROTON-1160',
                      'qpid-dispatch-router': 'decimal32 and decimal64 sent byte reversed: PROTON-1160',},
        'decimal64': {'ActiveMQ': 'decimal32 and decimal64 sent byte reversed: PROTON-1160',
                      'qpid-cpp': 'decimal64 not supported on qpid-cpp broker: QPIDIT-6, QPID-6328',
                      'apache-activemq-artemis': 'decimal32 and decimal64 sent byte reversed: PROTON-1160',
                      'qpid-dispatch-router': 'decimal32 and decimal64 sent byte reversed: PROTON-1160',},
        'decimal128': {'qpid-cpp': 'decimal128 not supported on qpid-cpp broker: QPIDIT-3, QPID-6328',
                       'qpid-dispatch-router': 'router with qpid or activemq broker',},
        'char': {'qpid-cpp': 'char not supported on qpid-cpp broker: QPIDIT-4, QPID-6328',
                 'apache-activemq-artemis': 'char types > 16 bits truncated on Artemis: ENTMQ-1685',
                 'qpid-dispatch-router': 'router with qpid or artemis broker',},
        'float': {'apache-activemq-artemis': '-NaN is stripped of its sign: ENTMQ-1686',},
        'double': {'apache-activemq-artemis': '-NaN is stripped of its sign: ENTMQ-1686',},
        }

    client_skip = {
        'decimal32': {'AmqpNetLite': 'Decimal types not supported: https://github.com/Azure/amqpnetlite/issues/223', },
        'decimal64': {'AmqpNetLite': 'Decimal types not supported: https://github.com/Azure/amqpnetlite/issues/223', },
        'decimal128': {'AmqpNetLite': 'Decimal types not supported: https://github.com/Azure/amqpnetlite/issues/223', },
    }

    def create_array(self, array_amqp_type, repeat):
        """
        Create a single test array for a given AMQP type from the test values for that type. It can be optionally
        repeated for greater number of elements.
        """
        test_array = [array_amqp_type]
        for _ in range(repeat):
            for val in self.type_map[array_amqp_type]:
                test_array.append(val)
        return test_array

    def create_test_arrays(self):
        """ Method to synthesize the test arrays from the values used in the previous type tests """
        test_arrays = []
        for array_amqp_type in self.type_map['array']:
            test_arrays.append(self.create_array(array_amqp_type, 1))
        print(test_arrays)
        return test_arrays

    def get_test_values(self, test_type):
        """
        Overload the parent method so that arrays can be synthesized rather than read directly.
        The test_type parameter is the AMQP type in this case
        """
        if test_type == 'array':
            return self.create_test_arrays()
        return super(AmqpPrimitiveTypes, self).get_test_values(test_type)


class AmqpTypeTestCase(qpid_interop_test.qit_common.QitTestCase):
    """Abstract base class for AMQP Type test cases"""

    def run_test(self, sender_addr, receiver_addr, amqp_type, test_value_list, send_shim, receive_shim):
        """
        Run this test by invoking the shim send method to send the test values, followed by the shim receive method
        to receive the values. Finally, compare the sent values with the received values.
        """
        if test_value_list: # len > 0
            test_name = 'amqp_types_test.%s.%s.%s' % (amqp_type, send_shim.NAME, receive_shim.NAME)
            # TODO: When Artemis can support it (in the next release), revert the queue name back to 'qpid-interop...'
            # Currently, Artemis only supports auto-create queues for JMS, and the queue name must be prefixed by
            # 'jms.queue.'
            queue_name = 'jms.queue.qpid-interop.%s' % test_name

            # Start the receive shim first (for queueless brokers/dispatch)
            receiver = receive_shim.create_receiver(receiver_addr, queue_name, amqp_type, str(len(test_value_list)))
            receiver.start()

            # Start the send shim
            sender = send_shim.create_sender(sender_addr, queue_name, amqp_type, dumps(test_value_list))
            sender.start()

            # Wait for both shims to finish
            sender.join_or_kill(qpid_interop_test.shims.THREAD_TIMEOUT)
            receiver.join_or_kill(qpid_interop_test.shims.THREAD_TIMEOUT)

            # Process return string from sender
            send_obj = sender.get_return_object()
            if send_obj is not None:
                if isinstance(send_obj, str):
                    if send_obj: # len > 0
                        self.fail('Send shim \'%s\':\n%s' % (send_shim.NAME, send_obj))
                else:
                    self.fail('Sender error: %s' % str(send_obj))

            # Process return string from receiver
            receive_obj = receiver.get_return_object()
            if isinstance(receive_obj, tuple):
                if len(receive_obj) == 2:
                    return_amqp_type, return_test_value_list = receive_obj
                    self.assertEqual(return_amqp_type, amqp_type,
                                     msg='AMQP type error:\n\n    sent:%s\n\n    received:%s' % \
                                     (amqp_type, return_amqp_type))
                    self.assertEqual(return_test_value_list, test_value_list, msg='\n    sent:%s\nreceived:%s' % \
                                     (test_value_list, return_test_value_list))
                else:
                    self.fail('Received incorrect tuple format: %s' % str(receive_obj))
            else:
                self.fail('Received non-tuple: %s' % str(receive_obj))


class TestOptions(qpid_interop_test.qit_common.QitCommonTestOptions):
    """Command-line arguments used to control the test"""

    def __init__(self, shim_map, default_xunit_dir=qpid_interop_test.qit_common.DEFUALT_XUNIT_LOG_DIR):
        super(TestOptions, self).__init__('Qpid-interop AMQP client interoparability test suite for AMQP simple types',
                                          shim_map, default_xunit_dir)
        type_group = self._parser.add_mutually_exclusive_group()
        type_group.add_argument('--include-type', action='append', metavar='AMQP-TYPE',
                                help='Name of AMQP type to include. Supported types:\n%s' %
                                sorted(AmqpPrimitiveTypes.type_map.keys()))
        type_group.add_argument('--exclude-type', action='append', metavar='AMQP-TYPE',
                                help='Name of AMQP type to exclude. Supported types: see "include-type" above')


class AmqpTypesTest(qpid_interop_test.qit_common.QitTest):
    """Top-level test for AMQP types"""

    TEST_NAME = 'amqp_types_test'

    def __init__(self):
        super(AmqpTypesTest, self).__init__(TestOptions, AmqpPrimitiveTypes)

    def _generate_tests(self):
        """Generate tests dynamically"""
        self.test_suite = unittest.TestSuite()
        # Create test classes dynamically
        for amqp_type in sorted(self.types.get_type_list()):
            if self.args.exclude_type is None or amqp_type not in self.args.exclude_type:
                test_case_class = self.create_testcase_class(amqp_type, product(self.shim_map.values(), repeat=2))
                self.test_suite.addTest(unittest.makeSuite(test_case_class))

    def create_testcase_class(self, amqp_type, shim_product):
        """
        Class factory function which creates new subclasses to AmqpTypeTestCase.
        """

        def __repr__(self):
            """Print the class name"""
            return self.__class__.__name__

        def add_test_method(cls, send_shim, receive_shim):
            """Function which creates a new test method in class cls"""

            @unittest.skipIf(self.types.skip_test(amqp_type, self.broker),
                             self.types.skip_test_message(amqp_type, self.broker))
            @unittest.skipIf(self.types.skip_client_test(amqp_type, send_shim.NAME),
                             self.types.skip_client_test_message(amqp_type, send_shim.NAME, 'SENDER'))
            @unittest.skipIf(self.types.skip_client_test(amqp_type, receive_shim.NAME),
                             self.types.skip_client_test_message(amqp_type, receive_shim.NAME, 'RECEIVER'))
            def inner_test_method(self):
                self.run_test(self.sender_addr,
                              self.receiver_addr,
                              self.amqp_type,
                              self.test_value_list,
                              send_shim,
                              receive_shim)

            inner_test_method.__name__ = 'test_%s_%s->%s' % (amqp_type, send_shim.NAME, receive_shim.NAME)
            setattr(cls, inner_test_method.__name__, inner_test_method)

        class_name = amqp_type.title() + 'TestCase'
        class_dict = {'__name__': class_name,
                      '__repr__': __repr__,
                      '__doc__': 'Test case for AMQP 1.0 simple type \'%s\'' % amqp_type,
                      'amqp_type': amqp_type,
                      'sender_addr': self.args.sender,
                      'receiver_addr': self.args.receiver,
                      'test_value_list': self.types.get_test_values(amqp_type)}
        new_class = type(class_name, (AmqpTypeTestCase,), class_dict)
        for send_shim, receive_shim in shim_product:
            add_test_method(new_class, send_shim, receive_shim)
        return new_class


#--- Main program start ---

if __name__ == '__main__':
    AMQP_TYPES_TEST = AmqpTypesTest()
    AMQP_TYPES_TEST.run_test()
    AMQP_TYPES_TEST.write_logs()
    if not AMQP_TYPES_TEST.get_result():
        sys.exit(1) # Errors or failures present
