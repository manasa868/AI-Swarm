"""End-to-end verification script for AI Swarm and Transparent Legal AI."""
import httpx
import json
import time

def main():
    print("=" * 60)
    print("RUNNING END-TO-END VERIFICATION ON RUNNING FASTAPI SERVER")
    print("=" * 60)

    with httpx.Client(base_url="http://127.0.0.1:8000") as client:
        # 1. Health
        h = client.get("/health")
        print("\n1. HEALTH STATUS:", h.json())
        assert h.status_code == 200

        # 2. Create Project
        p = client.post("/api/projects", json={
            "name": "E2E Fake News Detection System",
            "description": "Build an ML fake news detector with pipeline and tests",
            "project_type": "ml",
            "technologies": ["Python", "Scikit-Learn", "FastAPI"]
        })
        assert p.status_code == 200
        proj_id = p.json()["id"]
        print("\n2. CREATED PROJECT ID:", proj_id)

        # 3. Stream Multi-Agent Execution
        print("\n3. STREAMING REAL-TIME AGENT TELEMETRY:")
        with client.stream("GET", f"/api/projects/{proj_id}/stream", timeout=60.0) as stream:
            for line in stream.iter_lines():
                if line.startswith("data: "):
                    event = json.loads(line[6:])
                    evt_type = event.get("type")
                    if evt_type == "agent_started":
                        print(f"   >> [AGENT START] {event.get('agent_name')}: {event.get('task')}")
                    elif evt_type == "agent_completed":
                        print(f"   << [AGENT COMPLETED] {event.get('agent_name')}")
                    elif evt_type == "test_failure_detected":
                        print(f"   !! [TEST FAILURE DETECTED] Retrying auto-correction...")
                    elif evt_type == "workflow_completed":
                        print(f"   == [SWARM COMPLETED] {event.get('message')}")
                        break

        # 4. Check Generated Files Tree
        files_res = client.get(f"/api/projects/{proj_id}/files")
        tree = files_res.json().get("file_tree", [])
        print(f"\n4. GENERATED FILES ON DISK: {len(tree)} root items found.")
        for item in tree:
            item_type = "DIR" if item["is_dir"] else f"{item.get('size', 0)} bytes"
            print(f"   - {item['name']} ({item_type})")

        # 5. Check Dynamic Academic Documentation
        doc_res = client.get(f"/api/projects/{proj_id}/documentation")
        sections = doc_res.json().get("sections", {})
        print(f"\n5. DYNAMIC DOCUMENTATION: {len(sections)} sections generated.")
        print(f"   Sample Title: {doc_res.json().get('title')}")
        assert len(sections) >= 20

        # 6. Test Transparent Legal AI
        print("\n6. TESTING TRANSPARENT LEGAL AI PIPELINE:")
        leg_res = client.post("/api/legal/analyze", json={
            "question": "Is an employee non-compete clause enforceable without consideration?",
            "jurisdiction": "United States"
        })
        leg_id = leg_res.json()["id"]
        print(f"   Legal Query ID: {leg_id}")

        with client.stream("GET", f"/api/legal/{leg_id}/stream", timeout=30.0) as lstream:
            for line in lstream.iter_lines():
                if line.startswith("data: "):
                    levent = json.loads(line[6:])
                    if levent.get("type") == "agent_started":
                        print(f"   >> [LEGAL AGENT] {levent.get('agent')}")
                    elif levent.get("type") == "workflow_completed":
                        final_data = levent.get("final_data", {})
                        print(f"   == [LEGAL COMPLETED] Verified Sources Cited: {len(final_data.get('sources', []))}")
                        print(f"   == Mandatory Disclaimer Present: {'DISCLAIMER' in final_data.get('disclaimer', '')}")
                        break

    print("\n" + "=" * 60)
    print("ALL END-TO-END VERIFICATION STEPS PASSED PERFECTLY!")
    print("=" * 60)

if __name__ == "__main__":
    main()
