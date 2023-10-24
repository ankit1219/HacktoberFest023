########################################################################################################################
#
#TOPOLOGY :
# 				  ____________                               ______________
#  				 |            |                             |              |
# 				 |            |                             |              |   
#                |            |1/44                    1/44 |              |
#  				 | ELY_104    |-----------------------------|FX2_VPC_PRIMARY   
#                |  		  |                             |              |
#  				 |            |                             |              |
# 				 |____________|                             |______________|

# 
#Steps which is followed For this Bug:-
# Step 1:- Configured to the Switch(Heavenly-2)
# Step 2:- Create the monitor sessions in the box.
# Step 3:- Create source vlans on monistor session
# step 4:- verify getting Error message as " " and not causing any cores on the switch.
########################################################################################################################
from ats import tcl
from ats import aetest
from ats.log.utils import banner
import time
import logging
import os
import sys
import re
import pdb
import json
import pprint
import socket
import struct
import inspect
import CSCwe21361_lib as buglib
#import nxos.lib.nxos.util as util
#import ctsPortRoutines
#import pexpect
#import nxos.lib.common.topo as topo

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
global uut1, uut2        
global uut1_uut2_intf1, uut2_uut1_intf1



class ForkedPdb(pdb.Pdb):
    '''A Pdb subclass that may be used
    from a forked multiprocessing child1
    '''
    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = open('/dev/stdin')
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin



################################################################################
####                       COMMON SETUP SECTION                             ####
################################################################################
class common_setup(aetest.CommonSetup):
   @aetest.subsection
   def span_topo_parse(self,testscript,testbed,R1,R2):

       global uut1,uut2, tgen 

       global uut1_ixia_intf1, uut1_ixia_intf2, uut1_dest_intf1
       #global ixia_uut1_1, ixia_uut1_2
       #global ixia_chassis_ip, ixia_tcl_server, ixia_ixnetwork_tcl_server,ixia_username, ixia_reset_flag
       global uut1_uut2_intf1, uut2_uut1_intf1
        
       global custom
       global device1
       global ixia_sleep_time
       global uut_list

        
       uut1 = testbed.devices[R1]
       uut2 = testbed.devices[R2]
        
       uut_list = [uut1,uut2]
        
        ###  UUT 1 INTERFACES  ####
       uut1_uut2_intf1 = testbed.devices[R1].interfaces['uut1_uut2_intf1']
       uut2_uut1_intf1 = testbed.devices[R2].interfaces['uut2_uut1_intf1']
        #uut1_ixia_intf1 = testbed.devices[R1].interfaces['uut1_ixia_intf1']
        #uut1_ixia_intf2 = testbed.devices[R1].interfaces['uut1_ixia_intf2']
        #uut1_dest_intf1 = testbed.devices[R1].interfaces['uut1_dest_intf1']

       testscript.parameters['uut1_uut2_intf1'] = uut1_uut2_intf1
       testscript.parameters['uut2_uut1_intf1'] = uut2_uut1_intf1
        #testscript.parameters['uut1_ixia_intf2'] = uut1_ixia_intf2
        #testscript.parameters['uut1_dest_intf1'] = uut1_dest_intf1
        
       testscript.parameters['uut1_uut2_intf1'].name = testscript.parameters['uut1_uut2_intf1'].intf
       testscript.parameters['uut2_uut1_intf1'].name = testscript.parameters['uut2_uut1_intf1'].intf
        #testscript.parameters['uut1_ixia_intf2'].name = testscript.parameters['uut1_ixia_intf2'].intf
        #testscript.parameters['uut1_dest_intf1'].name = testscript.parameters['uut1_dest_intf1'].intf
        
        ###  Ixia interfaces  ####
        
        #ixia_uut1_1 = testbed.devices['ixia'].interfaces['ixia_uut1_1']
        #ixia_uut1_2 = testbed.devices['ixia'].interfaces['ixia_uut1_2']
        #
        #testscript.parameters['ixia_uut1_1'] = ixia_uut1_1
        #testscript.parameters['ixia_uut1_2'] = ixia_uut1_2
        #
        #testscript.parameters['ixia_uut1_1'].name = testscript.parameters['ixia_uut1_1'].intf
        #testscript.parameters['ixia_uut1_2'].name = testscript.parameters['ixia_uut1_2'].intf


       uut1_uut2_intf1 =uut1_uut2_intf1.intf
       uut2_uut1_intf1 =uut2_uut1_intf1.intf
        #uut1_dest_intf1 = uut1_dest_intf1.intf

        #ixia_uut1_1 = ixia_uut1_1.intf
        #ixia_uut1_2 = ixia_uut1_2.intf

        
       log.info("uut1_uut2_intf1=%s" % uut1_uut2_intf1)
       log.info("uut2_uut1_intf1=%s" % uut2_uut1_intf1)
        #log.info("uut1_dest_intf1=%s" % uut1_dest_intf1)
        #log.info("ixia_uut1_1=%s" % ixia_uut1_1)
        #log.info("ixia_uut1_2=%s" % ixia_uut1_2)
   
   @aetest.subsection
   def connect_to_devices(self,testscript,testbed,R1,R2):
       uut_list = [uut1, uut2]
       for uut in uut_list:
         log.info("Connecting to Device:%s" % uut.name)
         try:
             uut.connect()
             log.info("Connection to %s Successful..." % uut.name)
         except Exception as e:
             log.info("Connection to %s Unsuccessful " \
                        "Exiting error:%s" % (uut.name, e))
             self.failed(goto=['exit'])

################################################################################
###                          TESTCASE BLOCK                                  ###
################################################################################

###############################################################################################
# Test case 1 :
###############################################################################################
class config_plvan(aetest.Testcase):

    """Checking The bug(CSCwe21361)Arp not resolving after trigger"""
    @aetest.test
    def tc01_test(self):
        status_flags = []
        for uut in uut_list:
         buglib.feat(uut)
        # log.info(banner("Configure Private-Vlan")) 
        buglib.pvlan(uut1)
        
        # log.info(banner("Configure Interface"))
        buglib.intf(uut1_uut2_intf1,uut1)
        
        # log.info(banner("Configure Interface Vlan 1100"))
        buglib.vlan1(uut1)
        
        # log.info(banner("Configure Interface Vlan 1130 and Interface 1/44"))
        buglib.vlan2(uut2_uut1_intf1,uut2)
        
        # log.info(banner("Configure Interface Vlan1130"))
        buglib.int_vlan(uut2)
        
        # log.info(banner("Configure Interface Vlan1130"))
        # log.info("Configure Interface")
        # cmd = """interface Vlan1130
        #             no shutdown
        #             no ip redirects
        #             ip address 100.1.11.2/24
        #             """
        # uut2.configure(cmd)
        
        time.sleep(30)
        # log.info("Check CC")
        # cmd = """show consistency-checker membership vlan 1100 private-vlan"""
        # op = uut1.execute(cmd)
        output=buglib.cc(uut1)  
        match = re.search("FAILED",output)
        if match :
            log.info("FAILED")
            status_flags.append(0)
            # self.failed(goto=['common_cleanup'])
        else :	
            log.info("PASSED")
            status_flags.append(1)
        
        time.sleep(30)
        cmd = "ping 100.1.11.1"
        op=uut2.configure(cmd)
        if '64 bytes from' in op :
            log.info("PASSED")
            status_flags.append(1)
        else :	
            log.info("FAILED")
            status_flags.append(0)
            # self.failed(goto=['common_cleanup'])
            
        cmd = """sh ip arp detail"""
        op1=uut1.configure(cmd)
        op2=uut2.configure(cmd)
        match=re.search("Vlan1100",op1)
        match=re.search("Vlan1130",op2)
        if match:
            log.info("PASSED")
            status_flags.append(1)
        else :
            log.info("FAILED")
            status_flags.append(0)
            # self.failed(goto=['common_cleanup'])
            
        log.info("Disable Vlan 1100")
        cmd = """vlan 1100
                 no private-vlan primary 
                 no private-vlan association 1110,1120,1130
               """
        uut1.configure(cmd)
        if 1 in status_flags:
            self.passed("This Test Case is Passed")
        else:
            self.failed("This Test Case is Failed")
            self.failed(goto=['common_cleanup'])
            
##################################################################################################################################3
    """Trigger test case 2"""
    @aetest.test    
    def tc02_test(self):
        status_flags = []
        cmd = """vlan 1110
                 private-vlan primary
               private-vlan association 1120,1130
                 vlan 1120
               private-vlan community
                 vlan 1130
               private-vlan isolated"""
        uut1.configure(cmd)
        
        log.info("Configure Interface")
        cmd = """interface %s
                 switchport
                 switchport mode private-vlan host
                 switchport private-vlan host-association 1110 1130
                 no shutdown
              """%(uut1_uut2_intf1)
        uut1.configure(cmd)
        
        time.sleep(30)
        # log.info("Check consistency-checker")
        # cmd = """show consistency-checker membership vlan 1110 private-vlan"""
        # op = uut1.execute(cmd)
        output=buglib.cc(uut1)
        match = re.search("FAILED",output)
        if match :
            log.info("FAILED")
            status_flags.append(0)
            # self.failed(goto=['common_cleanup'])
        else :	
            log.info("PASSED")
            status_flags.append(1)
            
        if 1 in status_flags:
            self.passed("This Test Case is Passed")
        else:
            self.failed("This Test Case is Failed")
            self.failed(goto=['common_cleanup'])
###################################################################################################################################
    """Reverting the test case 1"""
    @aetest.test    
    def tc03_test(self):
      status_flags = []
      log.info("Configure Private-Vlan")
      cmd = """vlan 1110
               no private-vlan primary
               no private-vlan association 1120,1130
               vlan 1100
               private-vlan primary
               private-vlan association 1110,1120,1130
               vlan 1110,1120
               private-vlan community
               vlan 1130
               private-vlan isolated"""
      uut1.configure(cmd)
      
      # log.info("Configure Interface")
      buglib.intf(uut1_uut2_intf1,uut1)
      
      # log.info("Configure Interface")
      # cmd = """interface %s
      #          switchport
      #          switchport mode private-vlan host
      #          switchport private-vlan host-association 1100 1130
      #          no shutdown
      #       """%(uut1_uut2_intf1)
      # uut1.configure(cmd)
      time.sleep(30)
      log.info("Check consistency-checker")
      # cmd = """show consistency-checker membership vlan 1100 private-vlan"""
      # op = uut1.execute(cmd)
      output=buglib.cc(uut1)
      match = re.search("FAILED",output)
      # match = re.search("FAILED",op)
      if match :
          log.info("FAILED")
          status_flags.append(0)
          # self.failed(goto=['common_cleanup'])
      else :	
          log.info("PASSED")
          status_flags.append(1)
      
      log.info("Configure Interface Vlan 1130")
      cmd = """vlan 1130
            """
      uut2.configure(cmd)
      
      time.sleep(10)
      cmd = "ping 100.1.11.1"
      op=uut2.configure(cmd)
      if '64 bytes from' in op :
          log.info("PASSED")
          status_flags.append(1)
      else :	
          log.info("FAILED")
          status_flags.append(0)
          # self.failed(goto=['common_cleanup'])
          
      cmd = """sh ip arp detail
               """
      op1=uut1.configure(cmd)
      op2=uut2.configure(cmd)
      match=re.search("Vlan1100",op1)
      match=re.search("Vlan1130",op2)
      if match:
          log.info("PASSED")
          status_flags.append(1)
      else :
          log.info("FAILED")
          status_flags.append(0)
          # self.failed(goto=['common_cleanup'])
       
      log.info("Disabled Vlan 1100")
      cmd = """vlan 1100
               no private-vlan primary
               no private-vlan association 1110,1120,1130
             """
      uut1.configure(cmd)
      if 1 in status_flags:
          self.passed("This Test Case is Passed")
      else:
          self.failed("This Test Case is Failed")
          self.failed(goto=['common_cleanup'])
################################################################################
####                       COMMON CLEANUP SECTION                           ####
################################################################################

class common_cleanup(aetest.CommonCleanup):
   
   """clean up the vlan configuration, release the ports reserved and cleanup """
   @aetest.subsection
   def remove_configuration(self):
      log.info('remove vlan from both UUT1 and UUT2')
      cmd = """no vlan 1100,1110,1120,1130
               no interface vlan 1100
               no interface vlan 1110"""
      try:
          uut1.configure(cmd)
      except:
          log.error('Invalid CLI given: %s' % (cmd))
          log.error('Error with cli')
          log.error(sys.exc_info())
          self.failed(goto=['exit'])
          
      cmd = """no vlan 1130
               no interface vlan 1130"""
      try:
          uut2.configure(cmd)
      except:
          log.error('Invalid CLI given: %s' % (cmd))
          log.error('Error with cli')
          log.error(sys.exc_info())
          self.failed(goto=['exit'])
      
      log.info('remove configuration in {0}'.format(uut1))
      cmd = """ default interface %s """%(uut1_uut2_intf1)
      uut1.configure(cmd)
      
      log.info('remove configuration in {0}'.format(uut2))
      cmd = """ default interface %s """%(uut2_uut1_intf1)
      uut2.configure(cmd)


if __name__ == '__main__': 
    import argparse
    from ats import topology
    parser = argparse.ArgumentParser(description='standalone parser')
    parser.add_argument('--testbed', dest='testbed', type=topology.loader.load)
    parser.add_argument('--R1', dest='R1', type=str)
    parser.add_argument('--mode',dest = 'mode',type = str)
    args = parser.parse_known_args()[0]
    aetest.main(testbed=args.testbed,
            R1_name=args.R1,
            mode = args.mode,
            pdb = True)
