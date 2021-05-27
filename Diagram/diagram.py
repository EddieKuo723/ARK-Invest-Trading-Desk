from diagrams import Cluster, Diagram
from diagrams.aws.compute import ECS, EKS, Lambda
from diagrams.aws.integration import Eventbridge
from diagrams.aws.management import Cloudwatch

with Diagram("Event Processing", show=False):
    
    with Cluster("Event Flows"):
        CloudWatch = Eventbridge("Cloudwatch Event")
        workers = Lambda("Get Mail")
                              

    trading = Lambda("Trading Desk")
    with Cluster("Event Workers"):
    	sticker = [
    		Lambda("Sticker"),
    		Lambda("Sticker"),
    		Lambda("Sticker")
    	]
    	

    CloudWatch >> workers  >> trading >> sticker
    