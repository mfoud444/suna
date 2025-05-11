import requests
import concurrent.futures
import time
from typing import Dict, List, Optional

# Configuration
API_BASE = "https://mfoud444-docsp.hf.space/v1"
MAX_WORKERS = 5  # Number of concurrent tests
TIMEOUT = 30  # Seconds for request timeout
MAX_RETRIES = 2

def get_all_models() -> List[str]:
    """Fetch all available models from the API"""
    try:
        response = requests.get(f"{API_BASE}/models", timeout=TIMEOUT)
        response.raise_for_status()
        return [model["id"] for model in response.json()["data"]]
    except Exception as e:
        print(f"❌ Error getting models: {e}")
        return []

def get_model_info(model_name: str) -> Optional[Dict]:
    """Get information about a specific model"""
    try:
        response = requests.get(f"{API_BASE}/models/{model_name}", timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️ Error getting info for {model_name}: {e}")
        return None

def test_model_completion(model_name: str) -> Dict:
    """Test a model with a sample completion request"""
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! What can you do?"}
        ],
        "temperature": 0.7
    }
    
    result = {
        "model": model_name,
        "status": "FAILED",
        "response_time": 0,
        "response": None,
        "error": None
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_BASE}/chat/completions",
                json=payload,
                timeout=TIMEOUT
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result.update({
                    "status": "SUCCESS",
                    "response_time": response_time,
                    "response": response.json()
                })
                return result
            else:
                result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
        except requests.exceptions.Timeout:
            result["error"] = "Timeout"
        except Exception as e:
            result["error"] = str(e)
        
        if attempt < MAX_RETRIES - 1:
            time.sleep(1)  # Wait before retrying
    
    return result

def test_all_models():
    """Test all available models concurrently"""
    print("🔍 Fetching available models...")
    models = get_all_models()
    
    if not models:
        print("No models found!")
        return
    
    print(f"🚀 Found {len(models)} models. Testing with {MAX_WORKERS} concurrent workers...\n")
    
    # First get all model info sequentially to avoid flooding
    models_info = {}
    for model in models:
        info = get_model_info(model)
        if info:
            models_info[model] = info
    
    # Then test all models concurrently
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_model = {executor.submit(test_model_completion, model): model for model in models}
        
        for future in concurrent.futures.as_completed(future_to_model):
            model = future_to_model[future]
            try:
                result = future.result()
                results[model] = result
                
                if result["status"] == "SUCCESS":
                    print(f"✅ {model} succeeded in {result['response_time']:.2f}s")
                    if result["response"]:
                        content = result["response"]["choices"][0]["message"]["content"]
                        print(f"   Response: {content[:100]}...")
                else:
                    print(f"❌ {model} failed: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"⚠️ Exception testing {model}: {str(e)}")
                results[model] = {"status": "FAILED", "error": str(e)}
    
    # Print summary
    print("\n📊 Test Results Summary:")
    success_count = sum(1 for r in results.values() if r["status"] == "SUCCESS")
    print(f"Success: {success_count}/{len(models)} ({success_count/len(models):.1%})")
    
    print("\n🔧 Model Details:")
    for model, info in models_info.items():
        result = results.get(model, {})
        print(f"\nℹ️ {model}:")
        print(f"  - Owner: {info.get('owned_by', 'unknown')}")
        print(f"  - Description: {info.get('description', 'No description')[:80]}...")
        print(f"  - Status: {result.get('status', 'NOT TESTED')}")
        if "error" in result:
            print(f"  - Error: {result['error']}")

if __name__ == "__main__":
    start_time = time.time()
    test_all_models()
    print(f"\n⏱️ Total execution time: {time.time() - start_time:.2f} seconds")