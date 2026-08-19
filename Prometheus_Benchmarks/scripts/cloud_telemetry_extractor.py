#!/usr/bin/env python3
import numpy as np
import warnings
import argparse
from qiskit_ibm_runtime import QiskitRuntimeService

# Suppress standard IBM deprecation warnings for clean output
warnings.filterwarnings("ignore")

def calculate_shannon_entropy(counts):
    """Calculates the Shannon Entropy of a quantum measurement BitArray."""
    if not counts: return None, 0
    
    total_weight = sum(counts.values())
    if total_weight == 0: return None, 0
    
    probabilities = [v / total_weight for v in counts.values() if v > 0]
    entropy = -sum(p_i * np.log2(p_i) for p_i in probabilities)
    
    return entropy, total_weight

def extract_job_telemetry(job_id, token):
    print(f"[*] Authenticating with IBM Quantum Platform...")
    try:
        service = QiskitRuntimeService(
            channel="ibm_quantum_platform", 
            token=token
        )
    except Exception as e:
        print(f"[!] Authentication Failed. Please ensure your IBM token is correct.\nError: {e}")
        return

    print(f"[*] Fetching Job {job_id} from IBM servers...")
    try:
        job = service.job(job_id)
        result = job.result()
        
        counts = None
        
        # Handle Sampler V2 architecture (PUBs DataBins)
        if hasattr(result, '__getitem__') and len(result) > 0:
            pub_result = result[0] 
            for reg_name in dir(pub_result.data):
                if not reg_name.startswith("_"):
                    reg_data = getattr(pub_result.data, reg_name)
                    if hasattr(reg_data, "get_counts"):
                        counts = reg_data.get_counts()
                        break
        
        # Fallback for Legacy/Sampler V1 results
        if not counts and hasattr(result, 'get_counts'):
            counts = result.get_counts()

        if counts:
            entropy, shots = calculate_shannon_entropy(counts)
            print(f"\n[+] Extraction Successful!")
            print(f"    -> Total Shots: {shots}")
            print(f"    -> Shannon Entropy: {entropy:.4f} bits\n")
        else:
            print("[!] Error: Could not extract valid counts/bitstrings from the job payload.")

    except Exception as e:
        print(f"[!] API Fetch Error for Job {job_id}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and Verify Shannon Entropy from an IBM Quantum Job.")
    parser.add_argument("--job", type=str, required=True, help="The IBM Job ID to verify")
    args = parser.parse_args()
    
    # =========================================================
    # REVIEWERS: PASTE YOUR IBM QUANTUM API TOKEN BELOW
    # =========================================================
    IBM_TOKEN = "YOUR_IBM_TOKEN_HERE"
    
    if IBM_TOKEN == "YOUR_IBM_TOKEN_HERE":
        print("[!] WARNING: You must input your IBM API Token into the script to tunnel into the Qiskit Runtime API.")
    else:
        extract_job_telemetry(args.job, IBM_TOKEN)