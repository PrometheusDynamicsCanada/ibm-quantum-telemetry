"""
==============================================================================
 PROMETHEUS TELEMETRY DECODER
 Extracts and decompresses IBM Quantum SamplerV2 BitArray payloads.
==============================================================================
"""
import json
import zlib
import base64
import numpy as np
import sys

def decode_ibm_bitarray(hex_or_b64_str, num_bits, num_shots):
    """Decodes IBM's compressed bitstream format into a dictionary of classical counts."""
    try:
        raw_bytes = base64.b64decode(hex_or_b64_str)
        decompressed = zlib.decompress(raw_bytes)
        data = np.frombuffer(decompressed, dtype=np.uint8)
    except Exception as e:
        print(f"[!] Error decompressing payload: {e}")
        return {}

    # Reconstruct the bitstrings from the byte array
    bits = np.unpackbits(data, bitorder='little')
    bitstrings = []
    
    bytes_per_shot = (num_bits + 7) // 8
    bits_per_shot = bytes_per_shot * 8
    
    for i in range(num_shots):
        shot_bits = bits[i * bits_per_shot : i * bits_per_shot + num_bits]
        # Reverse to match quantum bit ordering convention (q3, q2, q1, q0...)
        bitstr = "".join(str(b) for b in shot_bits[::-1])
        bitstrings.append(bitstr)
        
    counts = {}
    for b in bitstrings:
        counts[b] = counts.get(b, 0) + 1
    return counts

def calculate_entropy(counts, total_shots):
    """Calculates the Shannon Entropy of the measurement distribution."""
    entropy = 0.0
    for val in counts.values():
        p = val / total_shots
        if p > 0:
            entropy -= p * np.log2(p)
    return entropy

def analyze_payload(filepath, num_bits=4, num_shots=100000):
    try:
        with open(filepath, "r") as f:
            result_data = json.load(f)
    except FileNotFoundError:
        print(f"[!] Could not find {filepath}. Ensure the JSON is in the same directory.")
        return

    try:
        pub_results = result_data["__value__"]["pub_results"]
    except KeyError:
        print("[!] Invalid JSON structure. Ensure this is an unmodified IBM SamplerV2 result payload.")
        return

    print(f"\n[*] ANALYZING PAYLOAD: {filepath}")
    print("==================================================")
    
    # Analyze Path A (SABRE Baseline)
    if len(pub_results) > 0:
        sabre_raw = pub_results[0]["__value__"]["data"]["__value__"]["fields"]["c"]["__value__"]["array"]["__value__"]
        sabre_counts = decode_ibm_bitarray(sabre_raw, num_bits=num_bits, num_shots=num_shots)
        sabre_entropy = calculate_entropy(sabre_counts, total_shots=num_shots)

        print(f"PATH A: QISKIT SABRE (OPTIMIZATION LEVEL 3)")
        print(f"Shannon Entropy: {sabre_entropy:.4f} Bits")
        print("Top 5 Measurement States:")
        for k, v in sorted(sabre_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  |{k}> : {v} shots")

    # Analyze Path B (Prometheus Engine)
    if len(pub_results) > 1:
        print("--------------------------------------------------")
        prom_raw = pub_results[1]["__value__"]["data"]["__value__"]["fields"]["c"]["__value__"]["array"]["__value__"]
        prom_counts = decode_ibm_bitarray(prom_raw, num_bits=num_bits, num_shots=num_shots)
        prom_entropy = calculate_entropy(prom_counts, total_shots=num_shots)

        print(f"PATH B: PROMETHEUS ENGINE (CUSTOM ML HEURISTIC)")
        print(f"Shannon Entropy: {prom_entropy:.4f} Bits")
        print("Top 5 Measurement States:")
        for k, v in sorted(prom_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  |{k}> : {v} shots")
            
    print("==================================================\n")

if __name__ == "__main__":
    # If a filename is passed via command line, use it. Otherwise, default to the 100k payload.
    target_file = sys.argv[1] if len(sys.argv) > 1 else "job-d8ru0e6gbcrc73f500g0-result.json"
    analyze_payload(target_file, num_bits=4, num_shots=100000)
