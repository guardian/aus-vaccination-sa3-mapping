import simplejson as json
import boto3
import os

AWS_KEY = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET = os.environ['AWS_SECRET_ACCESS_KEY']

if 'AWS_SESSION_TOKEN' in os.environ:
	AWS_SESSION = os.environ['AWS_SESSION_TOKEN']

def syncData(jsonObject,id):

	finalJson = json.dumps(jsonObject, indent=4)

	print("Connecting to S3")
	bucket = 'gdn-cdn'

	if 'AWS_SESSION_TOKEN' in os.environ:
		session = boto3.Session(
		aws_access_key_id=AWS_KEY,
		aws_secret_access_key=AWS_SECRET,
		aws_session_token = AWS_SESSION
		)
	else:
		session = boto3.Session(
		aws_access_key_id=AWS_KEY,
		aws_secret_access_key=AWS_SECRET,
		)


	s3 = session.resource('s3')

	key = "docsdata/{id}.json".format(id=id)
	object = s3.Object(bucket, key)
	object.put(Body=finalJson, CacheControl="max-age=30", ACL='public-read', ContentType="application/json")

	print("JSON is updated")

	print("data", "https://interactive.guim.co.uk/docsdata/{id}.json".format(id=id))
	print("https://interactive.guim.co.uk/embed/iframeable/2019/03/choropleth_map_maker_v5/html/index.html?key={id}".format(id=id))
	

def syncMap(settings, data, mapping, chartName):

	jsonDictObject = {
		"sheets":{
			"data":data,
			"settings":settings,
			"mapping":mapping
			}
	}

	#%% Sync

	syncData(jsonDictObject, chartName)
