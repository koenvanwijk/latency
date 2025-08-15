.PHONY: venv run clean
venv:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
run:
	python src/make_swimlane_from_excel.py examples/Teleop_Latency_Model_SO100_WebRTC_v3.xlsx out.png Typical
clean:
	rm -f out.png teleop_latency_swimlane_from_excel.png
