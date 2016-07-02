from threading import Thread
import rospy

# import Aldebaran API (must be in PYTHONPATH):
try:
    from naoqi import ALProxy
except ImportError:
    raise RuntimeError("Error importing NaoQI. Please make sure that Aldebaran's NaoQI API is in your PYTHONPATH.")

import rospy
import sys
import actionlib
from naoqi_bridge_msgs.msg import BodyPoseAction, BodyPoseGoal

class NaoqiNode(Thread):
    """
    A ROS Node wrapper that can help you connect to NAOqi and deal with ROS shutdown
    To start your node, just call:
    my_node = MyNode('my_node')
    my_node.start() # that will spawn your node in a thread (and run whatever is in the run() function
    rospy.spin()
    # when killing ROS, the node will automatically stop its main loop, exit, and then unsubscribe from ALMemory events
    # and call whatever you have in unsubscribe()
    Then, if your node needs to process data, you just needs to have a run function:
    def run(Self):
        #do some initialization
        while self.is_looping():
            # do something
        # do some post processing
    """
    
            
            
    def __init__(self, name):
        """
        :param name: the name of the ROS node
        """
        super(NaoqiNode, self).__init__()

        # A distutils.version.LooseVersion that contains the current verssion of NAOqi we're connected to
        self.__naoqi_version = None
        self.__name = name

        ## NAOqi stuff
        # dict from a modulename to a proxy
        self.__proxies = {}

        # Initialize ros, before getting parameters.
        rospy.init_node(self.__name)

        # If user has set parameters for ip and port use them as default
        default_ip = rospy.get_param("~pip", "127.0.0.1")
        default_port = rospy.get_param("~pport", 9559)

        # get connection from command line:
        from argparse import ArgumentParser
        parser = ArgumentParser()
        parser.add_argument("--pip", dest="pip", default=default_ip,
                          help="IP/hostname of parent broker. Default is 127.0.0.1.", metavar="IP")
        parser.add_argument("--pport", dest="pport", default=default_port, type=int,
                          help="port of parent broker. Default is 9559.", metavar="PORT")

        import sys
        args = parser.parse_args(args=rospy.myargv(argv=sys.argv)[1:])
        self.pip = args.pip
        self.pport = args.pport

        ## ROS stuff
        self.__stop_thread = False
        # make sure that we unregister from everything when the module dies
        rospy.on_shutdown(self.__on_ros_shutdown)

    def __on_ros_shutdown(self):
        """
        Callback function called whenever rospy.spin() stops
        """
        rospy.loginfo('Stopping ' + self.__name)

        self.__stop_thread = True
        # wait for the thread to be done
        if self.is_alive():
            self.join()

        rospy.loginfo(self.__name + ' stopped')

    def run(self):
        print (self.get_version())
        self.pose()
      #  self.pose(self)
        # code example
        #do some initialization
      #  while self.is_looping():
      #      print ('t')
        # do some post processing
       

    def is_looping(self):
        """
        :return: whether the thread is supposed to be running
        """
        return not self.__stop_thread

    def get_proxy(self, name, warn=True):
        """
        Returns a proxy to a specific module. If it has not been created yet, it is created
        :param name: the name of the module to create a proxy for
        :return: a proxy to the corresponding module
        """
        if name in self.__proxies and self.__proxies[name] is not None:
            return self.__proxies[name]

        proxy = None
        try:
            proxy = ALProxy(name,self.pip,self.pport)
        except RuntimeError,e:
            if warn:
                rospy.logerr("Could not create Proxy to \"%s\". \nException message:\n%s",name, e)

        self.__proxies[name] = proxy
        return proxy

    def get_version(self):
        """
        Returns the NAOqi version.
        A proxy for ALMemory is automatically created if needed as self.memProxy.
        You can then simply have code that runs or not depending on the NAOqi version.
        E.g. if distutils.version.LooseVersion('1.6') < get_version()    ....
        :return: a distutils.version.LooseVersion object with the NAOqi version
        """
        if self.__naoqi_version is None:
            proxy = self.get_proxy('ALMemory')
            if proxy is None:
                # exiting is bad but it should not happen
                # except maybe with NAOqi versions < 1.6 or future ones
                # in which case we will adapt that code to call the proper
                # version function
                exit(1)

            from distutils.version import LooseVersion
            self.__naoqi_version = LooseVersion(proxy.version())

        return self.__naoqi_version

    def pose(self):
         pose = 'crouch'
         poseClient = actionlib.SimpleActionClient("body_pose", BodyPoseAction)
         if not poseClient.wait_for_server(rospy.Duration(3.0)):
             rospy.logfatal("Could not connect to required \"body_pose\" action server, is the pose_manager node running?");
             rospy.signal_shutdown();

         goal = BodyPoseGoal
         goal.pose_name = str(pose)
         rospy.loginfo("Calling pose_manager for pose %s...", goal.pose_name)

 
         poseClient.send_goal_and_wait(goal, rospy.Duration(5.0))
         #TODO: check for errors
         exit(0)
        

if __name__ == '__main__':
    
    
     my_node = NaoqiNode('my_node')
    
     my_node.start() # that will spawn your node in a thread (and run whatever is in the run() function
     rospy.spin()
    
