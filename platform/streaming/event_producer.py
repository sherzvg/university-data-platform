from kafka import KafkaProducer
import json, random, time, uuid
from datetime import datetime, timezone

producer = KafkaProducer(
    bootstrap_servers="localhost:9094",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode("utf-8"),
)

EVENT_TYPES = ["entered_classroom", "left_classroom", "submitted_assignment"]
ROOMS = [f"room_{i:03d}" for i in range(50)]
STUDENTS = [f"stu_{i:04d}" for i in range(500)]

print("Producing events to topic 'campus.events.v1'...")
try:
    while True:
        event = {
            "event_id": str(uuid.uuid4()),
            "event_ts": datetime.now(timezone.utc).isoformat(),
            "event_type": random.choice(EVENT_TYPES),
            "student_id": random.choice(STUDENTS),
            "room_id": random.choice(ROOMS),
        }
        producer.send("campus.events.v1", key=event["student_id"], value=event)
        time.sleep(random.uniform(0.05, 0.3))
except KeyboardInterrupt:
    producer.flush()
    print("Stopped.")
