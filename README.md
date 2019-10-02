
pip install -r requirements.txt
python app.py


API ENDPOINT

1. Post a message
localhost:5000/message [POST]
body:
{
	"topic":"warung_pintar",
	"message":"warung pintar code challenge"
}

2. Get all message
localhost:5000/message [GET]


3. Display message in real time
http://localhost:5000/
Please subscribe a topic based on "topic" body in point (1)


