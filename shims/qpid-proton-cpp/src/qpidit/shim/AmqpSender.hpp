/*
 *
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 *
 */

#ifndef SRC_QPIDIT_SHIM_AMQPSENDER_HPP_
#define SRC_QPIDIT_SHIM_AMQPSENDER_HPP_

#include <iomanip>
#include <json/value.h>
#include "proton/handler.hpp"
#include "proton/message.hpp"
#include "qpidit/QpidItErrors.hpp"

namespace qpidit
{
    namespace shim
    {

        class AmqpSender : public proton::handler
        {
        protected:
            const std::string _brokerUrl;
            const std::string _amqpType;
            const Json::Value _testValues;
            uint32_t _msgsSent;
            uint32_t _msgsConfirmed;
            uint32_t _totalMsgs;
        public:
            AmqpSender(const std::string& brokerUrl, const std::string& amqpType, const Json::Value& testValues);
            virtual ~AmqpSender();
            void on_start(proton::event &e);
            void on_sendable(proton::event &e);
            void on_delivery_accept(proton::event &e);
            void on_disconnect(proton::event &e);
        protected:
            proton::message& setMessage(proton::message& msg, const Json::Value& testValue);

            static std::string bytearrayToHexStr(const char* src, int len);
            static void revMemcpy(char* dest, const char* src, int n);
            static void uint64ToChar16(char* dest, uint64_t upper, uint64_t lower);

            static proton::value extractProtonValue(const Json::Value& val);
            //static Json::Value::ValueType getArrayType(const Json::Value& val);
            static void processArray(std::vector<proton::value>& array, const Json::Value& testValues);
            static void processList(std::vector<proton::value>& list, const Json::Value& testValues);
            static void processMap(std::map<std::string, proton::value>& map, const Json::Value& testValues);

            template<size_t N> static void hexStringToBytearray(proton::byte_array<N>& ba, const std::string s, size_t fromArrayIndex = 0, size_t arrayLen = N) {
                for (size_t i=0; i<arrayLen; ++i) {
                    ba[fromArrayIndex + i] = (char)std::strtoul(s.substr(2*i, 2).c_str(), NULL, 16);
                }
            }

            // Set message body to floating type T through integral type U
            // Used to convert a hex string representation of a float or double to a float or double
            template<typename T, typename U> void setFloatValue(proton::message& msg, const std::string& testValueStr) {
                try {
                    U ival(std::strtoul(testValueStr.data(), NULL, 16));
                    msg.body(T(*reinterpret_cast<T*>(&ival)));
                } catch (const std::exception& e) { throw qpidit::InvalidTestValueError(_amqpType, testValueStr); }
            }

            template<typename T> void setIntegralValue(proton::message& msg, const std::string& testValueStr, bool unsignedVal) {
                try {
                    T val(unsignedVal ? std::strtoul(testValueStr.data(), NULL, 16) : std::strtol(testValueStr.data(), NULL, 16));
                    msg.body(val);
                } catch (const std::exception& e) { throw qpidit::InvalidTestValueError(_amqpType, testValueStr); }
            }

            template<typename T> void setStringValue(proton::message& msg, const std::string& testValueStr) {
                try {
                    T val(testValueStr);
                    msg.body(val);
                } catch (const std::exception& e) { throw qpidit::InvalidTestValueError(_amqpType, testValueStr); }
            }
        };

    } /* namespace shim */
} /* namespace qpidit */

#endif /* SRC_QPIDIT_SHIM_AMQPSENDER_HPP_ */
