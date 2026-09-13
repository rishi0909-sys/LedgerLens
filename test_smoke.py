import requests
import time

def run_smoke_test():
    print("Running end-to-end smoke test...")
    
    # 1. Health check
    try:
        res = requests.get("http://localhost:8000/health")
        assert res.status_code == 200, f"Health check failed: {res.status_code}"
        print("✅ Health check passed")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
        
    # 2. Get Candidate Queue
    try:
        res = requests.get("http://localhost:8000/api/ml/candidate-queue")
        assert res.status_code == 200
        data = res.json()
        assert "window_id" in data
        assert "candidates" in data
        assert len(data["candidates"]) > 0
        print("✅ Candidate Queue endpoint passed")
    except Exception as e:
        print(f"❌ Candidate Queue endpoint failed: {e}")
        return
        
    # 3. Ask RL Agent for Next Investigation
    try:
        req_data = {
            "candidates": data["candidates"],
            "remaining_budget": 5,
            "budget_limit": 5,
            "cumulative_discoveries": 0
        }
        res = requests.post("http://localhost:8000/api/ml/investigation-next", json=req_data)
        assert res.status_code == 200
        rl_data = res.json()
        assert "selected_transaction_id" in rl_data
        print(f"✅ RL Agent selected case: {rl_data['selected_transaction_id']}")
    except Exception as e:
        print(f"❌ RL Agent endpoint failed: {e}")
        return
        
    print("All smoke tests passed! 🎉")

if __name__ == "__main__":
    run_smoke_test()
