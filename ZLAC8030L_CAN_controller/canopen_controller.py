"""
BSD 3-Clause License
Copyright (c) 2022, Mohamed Abdelkader Zahana
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import os
import logging
import traceback
import time
import canopen
from scipy.fft import idstn

# Set logging level. logging.DEBUG will log/print all messages
logging.basicConfig(level=logging.DEBUG)

class MotorController:
   """MotorController
   Implements convenience methods to monitor and operate ZLAC8030L drivers
   """
   def __init__(self, channel='can0', bustype='socketcan', bitrate=250000, node_ids=None, debug=False):
      """
      @brief Creates and connects to CAN bus

      Parameters
      --
      @param channel CAN channel
      @param bustype CAN bus type. See Python canopen & can docs
      @param bitrate CAN bus bitrate. See Python canopen & can docs
      @param node_ids List of expected node IDs. If None, will continue with the available nodes. If specified, will exit if an expected node does not exist onthe bus 
      @debug Print logging/debug messages
      """
      self._debug = debug
      self._network = canopen.Network() # CAN bus
      self._channel = channel
      self._bustype = bustype
      self._bitrate = bitrate
      self._node_ids = node_ids

      # Following the eaxmple in https://github.com/christiansandberg/canopen/blob/master/examples/simple_ds402_node.py
      # Try to connect
      try:
         self._network.connect(bustype=self._bustype, channel=self._channel, bitrate=self._bitrate)
         self._network.check()

         # Detecet connected nodes
         # This will attempt to read an SDO from nodes 1 - 127
         self._network.scanner.search()
         # We may need to wait a short while here to allow all nodes to respond
         time.sleep(0.05)
         logging.info('Available nodes: %s', self._network.scanner.nodes)

         if node_ids is not None: # User specified the expected nodes that should be available
            for id in node_ids:
               # Sanity checks
               if not type(id) is int:
                  logging.error("Only integers are allowed for node ID") 
                  raise TypeError("Only integers are allowed for node ID")
               if id < 0 or id > 127:
                  logging.error("Node ID %s is not in the range [0,127]", id) 
                  raise Exception("Node ID {} is not in the range [0,127]".format(id))

               if not (id in self._network.scanner.nodes):
                  logging.error("Node ID %s is not available in %s",id, self._network.scanner.nodes)
                  raise Exception("Node ID {} is not available in {}".format(id, self._network.scanner.nodes)) 

      except Exception as e:
         exc_type, exc_obj, exc_tb = sys.exc_info()
         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
         logging.error('%s %s %s', exc_type, fname, exc_tb.tb_lineno)
         traceback.print_exc()
      finally:
         # Disconnect from CAN bus
         logging.error('going to exit... stopping...')
         if self._network:
            for node_id in self._network:
               node =self._network[node_id]
               node.nmt.state = 'PRE-OPERATIONAL'
               node.nmt.stop_node_guarding()
               self._network.sync.stop()
               self._network.disconnect()
               return
      
      # Reaching here means that CAN connection went well.

   def disconnectNetwork(self):
      """
      Disconnects the entire CAN network
      """
      logging.error('going to exit... stopping...')
      if self._network:
         for node_id in self._network:
            node =self._network[node_id]
            node.nmt.state = 'PRE-OPERATIONAL'
            node.nmt.stop_node_guarding()
            self._network.sync.stop()
            self._network.disconnect()
            return

   def setNMTPreOperation(self, node_ids):
      """
      Sets node.nmt.state to 'PRE-OPERATIONAL'. Raises exceptions on failures

      Parameters
      --
      @param node_id list of Node IDs. List of [int]
      """
      # Sanity checks
      if not type(node_ids) is list:
         raise Exception("[enableOperation] node_ids should be a list of at least one node ID")

      # TODO Needs implementation

   def enableOperation(self, node_ids):
      """
      Sets node.state to 'OPERATION ENABLED'. Raises exceptions on failures

      Parameters
      --
      @param node_id list of Node IDs. List of [int]
      """
      # Sanity checks
      if not type(node_ids) is list:
         raise Exception("[enableOperation] node_ids should be a list of at least one node ID")

      for id in node_ids:
         # Sanity check
         if not type(id) is int:
            raise Exception("[enableOperation] Node ID {} is not int".format(id))

         if not id in self._network:
            raise Exception("Node ID {} is not available. Skipping operation enabling.".format(id))

         node = self._network[id]
         timeout = time.time() + 15
         node.state = 'OPERATION ENABLED'
         while node.state != 'OPERATION ENABLED':
            if time.time() > timeout:
               raise Exception('Timeout when trying to change state of node ID {}'.format(id))
         time.sleep(0.001)

   def getOperationStatus(self, node_id):
      """
      Gets the operation status (not network status), of a particular node

      Parameters
      --
      @param node_id Node ID [int]

      Returns
      --
      @return status Operation status. Raises an exception on error
      """
      # Sanity checks
      # TODO Needs implementation
      pass

   def getNMTStatus(self, node_id):
      """
      Gets the NMT status of a particular node
      
      Parameters
      --
      @param node_id Node ID [int]

      Returns
      --
      @return status NMT status. Raises an exception on error
      """
      # Sanity checks
      # TODO Needs implementation
      pass

   def getVelocity(self, node_id):
      """
      Gets velocity value of a particular node

      Parameters
      --
      @param node_id Node ID [int]

      Returns
      --
      @return vel Velocity in m/s. Raises an exception on error
      """
      # Sanity checks
      # TODO Needs implementation
      pass

   def getEncoder(self, node_id):
      """
      Gets encoder value of a particular node

      Parameters
      --
      @param node_id Node ID [int]

      Returns
      --
      @return enc Encoder value. Raises an exception on error
      """
      # Sanity checks
      # TODO Needs implementation
      pass

   def setTargetVelocity(self, node_id, vel=0.0):
      """
      Sends target velocity value of a particular node. Raises exception on failures

      Parameters
      --
      @param node_id Node ID [int]
      @param vel Velocity value [what is the type?]
      """
      # Sanity checks
      # TODO Needs implementation
      pass