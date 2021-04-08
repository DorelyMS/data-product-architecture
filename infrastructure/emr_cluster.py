import yaml
import boto3

def read_yaml(credentials_file): 
	"""
	Funcion para leer archivo config
	"""
	with open(credentials_file, "r") as cred:
		res = yaml.safe_load(cred)

	return res

def get_s3_credentials(credentials_file):
	"""
	Funcion que devuelve credenciales de aws para bucket
	"""

	cred = read_yaml(credentials_file)['default']

	return cred


def get_s3_resource(cred_path="./conf/local/credentials.yaml"):
	"""
	Esta función regresa un resource de S3 para poder guardar datos en el bucket
	"""

	s3_creds = get_s3_credentials(cred_path)

	session = boto3.Session(
	    aws_access_key_id=s3_creds['aws_access_key_id'],
	    aws_secret_access_key=s3_creds['aws_secret_access_key']
	)

	client = session.client('emr')

	return client

if __name__ == "__main__":

	client = get_s3_resource()

	response = client.run_job_flow(
	    Name='cluster_spark',
	    LogUri='s3://aws-logs-brunocgf-us-east-2/elasticmapreduce/',
	    ReleaseLabel='emr-5.32.0',
	    Applications=[
	        {
	            'Name': 'Spark'
	        },
	    ],
	    Instances={
	        'InstanceGroups': [
	            {
	                'Name': 'Master',
	                'Market': 'ON_DEMAND',
	                'InstanceRole': 'MASTER',
	                'InstanceType': 'm5.xlarge',
	                'InstanceCount': 1,
	            },
	            {
	                'Name': 'Slave',
	                'Market': 'ON_DEMAND',
	                'InstanceRole': 'CORE',
	                'InstanceType': 'm5.xlarge',
	                'InstanceCount': 1,
	            },
	        ],
	        'Ec2KeyName': 'id_aws',
	        'KeepJobFlowAliveWhenNoSteps': True,
	        'TerminationProtected': False,
	        'Ec2SubnetId': 'subnet-076ec16c',
	    },
	    # Steps=[
	    #     {
	    #         'Name': 'file-copy-step',
	    #         'ActionOnFailure': 'TERMINATE_JOB_FLOW',
	    #         'HadoopJarStep': {	            
     #                'Jar': 's3://Snapshot-jar-with-dependencies.jar',
     #                'Args': ['test.xml', 'emr-test', 'kula-emr-test-2']
     #            }
	    #     },
	    # ],
	    # VisibleToAllUsers=True,
	    JobFlowRole='EMR_EC2_DefaultRole',
	    ServiceRole='EMR_DefaultRole',
	)