# Deployment Memory Footprint & Model Catalog

This catalog details the complete deployment memory footprint for each model setup, combining:
1. **Base Model Weights**
2. **Vision Multimodal Projector (`mmproj`)**
3. **Speculative Decoding Draft Head / Model (`mtp` / DSpark)**
4. **8-Bit KV Cache at Specified Context Size**

---

## 💡 VRAM-Spar-Hebel: Kontextgröße mit `-c` gezielt reduzieren

> [!TIP]
> **Warum ist das Flag `-c` so wichtig?**  
> Bei modernen Modellen mit 131k oder 262k Tokens belegt der KV-Cache bei voller Länge oft **mehr VRAM als das Modell selbst**!  
> Beispiel **Qwen 3.8 27B**: Das 4-Bit Modell (`IQ4_XS`) wiegt nur 13,27 GiB – der KV-Cache bei 262k Tokens belegt jedoch zusätzliche **32,50 GiB** VRAM!
> 
> Mit dem Flag `-c <tokens>` beim Start von `llama-server` kannst du den maximalen Kontext auf genau das Maß begrenzen, das du tatsächlich benötigst:
> - **Halbierung der Kontextgröße (`-c`) $\rightarrow$ Halbierung des KV-Cache-Speicherbedarfs!**
> - **Sinnvolle Werte (Zweierpotenzen):**
>   - `-c 262144` (262k = Standard / Voll): Maximale Dokumenten- & Codebase-Länge.
>   - `-c 131072` (128k = Sweet Spot): **50 % KV-Cache-Ersparnis** *(spart bei Qwen 27B sofort **16,25 GiB VRAM!**)*.
>   - `-c 65536` (64k = Laptop & 24GB GPUs): **75 % KV-Cache-Ersparnis** *(spart bei Qwen 27B **24,37 GiB VRAM**, wodurch Qwen 27B IQ4_XS mit 23,55 GiB komplett in eine 24-GB-GPU wie die RTX 3090/4090 passt!)*.
>   - `-c 32768` (32k = Standard Chat & Alltags-Tasks): Minimaler Speicherverbrauch (~4 GiB KV-Cache).

---

## 🚀 Full Deployment Memory Footprint Table

*All sizes in binary gigabytes (GiB) / mebibytes (MiB). Ranked by total deployment memory footprint.*

| # | Deployment Setup | Base Model Size | Fitting `mmproj` | Fitting `mtp` (Draft) | Est. 8-Bit KV Cache | 💾 Total Deployment Memory | Source Repo |
|---|---|---|---|---|---|---|---|
| **1a** | **Qwen 3.8 27B (Q8_K_XL)**<br>*(Full Context 262k)* | 29.30 GiB<br>`Qwen3.8-27B-UD-Q8_K_XL.gguf` | 888.0 MiB<br>`mmproj-BF16.gguf` | 1.28 GiB<br>`mtp-Qwen3.8-27B-Q4_0.gguf` | **32.50 GiB**<br>*(262k context)* | 🔥 **63.94 GiB** | [unsloth/Qwen3.8-27B-GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF) |
| **1b** | **Qwen 3.8 27B (Q8_K_XL)**<br>*(`-c 131072` / 128k Context)* | 29.30 GiB<br>`Qwen3.8-27B-UD-Q8_K_XL.gguf` | 888.0 MiB<br>`mmproj-BF16.gguf` | 1.28 GiB<br>`mtp-Qwen3.8-27B-Q4_0.gguf` | **16.25 GiB**<br>*(128k context)* | ⚡ **47.69 GiB** *(50% KV)* | [unsloth/Qwen3.8-27B-GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF) |
| **2a** | **Qwen 3.8 27B (Q4_K_XL)**<br>*(Full Context 262k)* | 16.35 GiB<br>`Qwen3.8-27B-UD-Q4_K_XL.gguf` | 888.0 MiB<br>`mmproj-BF16.gguf` | 1.28 GiB<br>`mtp-Qwen3.8-27B-Q4_0.gguf` | **32.50 GiB**<br>*(262k context)* | ⚡ **51.00 GiB** | [unsloth/Qwen3.8-27B-GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF) |
| **2b** | **Qwen 3.8 27B (Q4_K_XL)**<br>*(`-c 131072` / 128k Context)* | 16.35 GiB<br>`Qwen3.8-27B-UD-Q4_K_XL.gguf` | 888.0 MiB<br>`mmproj-BF16.gguf` | 1.28 GiB<br>`mtp-Qwen3.8-27B-Q4_0.gguf` | **16.25 GiB**<br>*(128k context)* | ⚡ **34.75 GiB** *(50% KV)* | [unsloth/Qwen3.8-27B-GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF) |
| **2c** | **Qwen 3.8 27B (Q4_K_XL)**<br>*(`-c 65536` / 64k Context)* | 16.35 GiB<br>`Qwen3.8-27B-UD-Q4_K_XL.gguf` | 888.0 MiB<br>`mmproj-BF16.gguf` | 1.28 GiB<br>`mtp-Qwen3.8-27B-Q4_0.gguf` | **8.13 GiB**<br>*(64k context)* | 🟢 **26.63 GiB** *(25% KV)* | [unsloth/Qwen3.8-27B-GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF) |
| **3a** | **Qwen 3.8 27B (IQ4_XS)**<br>*(Full Context 262k)* | 13.27 GiB<br>`Qwen3.8-27B-UD-IQ4_XS.gguf` | 888.0 MiB<br>`mmproj-BF16.gguf` | 1.28 GiB<br>`mtp-Qwen3.8-27B-Q4_0.gguf` | **32.50 GiB**<br>*(262k context)* | ⚡ **47.92 GiB** | [unsloth/Qwen3.8-27B-GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF) |
| **3b** | **Qwen 3.8 27B (IQ4_XS)**<br>*(`-c 131072` / 128k Context)* | 13.27 GiB<br>`Qwen3.8-27B-UD-IQ4_XS.gguf` | 888.0 MiB<br>`mmproj-BF16.gguf` | 1.28 GiB<br>`mtp-Qwen3.8-27B-Q4_0.gguf` | **16.25 GiB**<br>*(128k context)* | 🟢 **31.67 GiB** *(50% KV)* | [unsloth/Qwen3.8-27B-GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF) |
| **3c** | **Qwen 3.8 27B (IQ4_XS)**<br>*(`-c 65536` / 64k Context)* | 13.27 GiB<br>`Qwen3.8-27B-UD-IQ4_XS.gguf` | 888.0 MiB<br>`mmproj-BF16.gguf` | 1.28 GiB<br>`mtp-Qwen3.8-27B-Q4_0.gguf` | **8.13 GiB**<br>*(64k context)* | 🟢 **23.55 GiB** *(Fits 24GB GPU!)* | [unsloth/Qwen3.8-27B-GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF) |
| **4a** | **Gemma 4 26B-A4B (Q4_K_XL)**<br>*(Full Context 262k SWA)* | 13.27 GiB<br>`gemma-4-26B-A4B-it-qat-UD-Q4_K_XL.gguf` | 1.11 GiB<br>`mmproj-BF16.gguf` | 440.4 MiB (Q8) / 240.3 MiB (Q4)<br>`mtp-gemma-4-26B-A4B-it-Q8_0.gguf` | **2.60 GiB**<br>*(262k context SWA)* | ⚡ **17.41 GiB** *(Q8 MTP)*<br>**17.21 GiB** *(Q4 MTP)* | [unsloth/gemma-4-26B-A4B-it-qat-GGUF](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-qat-GGUF) |
| **4b** | **Gemma 4 26B-A4B (Q4_K_XL)**<br>*(`-c 131072` / 128k Context)* | 13.27 GiB<br>`gemma-4-26B-A4B-it-qat-UD-Q4_K_XL.gguf` | 1.11 GiB<br>`mmproj-BF16.gguf` | 440.4 MiB (Q8) / 240.3 MiB (Q4)<br>`mtp-gemma-4-26B-A4B-it-Q8_0.gguf` | **1.30 GiB**<br>*(128k context SWA)* | ⚡ **16.11 GiB** *(Q8 MTP)*<br>**15.91 GiB** *(Q4 MTP)* | [unsloth/gemma-4-26B-A4B-it-qat-GGUF](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-qat-GGUF) |
| **5a** | **Gemma 4 12B (Q8_K_XL)**<br>*(Full Context 262k SWA)* | 12.70 GiB<br>`gemma-4-12b-it-UD-Q8_K_XL.gguf` | 167.0 MiB<br>`mmproj-BF16.gguf` | 443.6 MiB<br>`mtp-gemma-4-12b-it-Q8_0.gguf` | **2.16 GiB**<br>*(262k context SWA)* | ⚡ **15.45 GiB** | [unsloth/gemma-4-12b-it-GGUF](https://huggingface.co/unsloth/gemma-4-12b-it-GGUF) |
| **5b** | **Gemma 4 12B (Q8_K_XL)**<br>*(`-c 131072` / 128k Context)* | 12.70 GiB<br>`gemma-4-12b-it-UD-Q8_K_XL.gguf` | 167.0 MiB<br>`mmproj-BF16.gguf` | 443.6 MiB<br>`mtp-gemma-4-12b-it-Q8_0.gguf` | **1.08 GiB**<br>*(128k context SWA)* | ⚡ **14.37 GiB** | [unsloth/gemma-4-12b-it-GGUF](https://huggingface.co/unsloth/gemma-4-12b-it-GGUF) |
| **6a** | **Gemma 4 12B QAT (Q4_K_XL)**<br>*(Full Context 262k SWA)* | 6.26 GiB<br>`gemma-4-12B-it-qat-UD-Q4_K_XL.gguf` | 167.0 MiB<br>`mmproj-BF16.gguf` | 443.6 MiB<br>`mtp-gemma-4-12B-it-Q8_0.gguf` | **2.16 GiB**<br>*(262k context SWA)* | 🟢 **9.01 GiB** | [unsloth/gemma-4-12B-it-qat-GGUF](https://huggingface.co/unsloth/gemma-4-12B-it-qat-GGUF) |
| **6b** | **Gemma 4 12B QAT (Q4_K_XL)**<br>*(`-c 131072` / 128k Context)* | 6.26 GiB<br>`gemma-4-12B-it-qat-UD-Q4_K_XL.gguf` | 167.0 MiB<br>`mmproj-BF16.gguf` | 443.6 MiB<br>`mtp-gemma-4-12B-it-Q8_0.gguf` | **1.08 GiB**<br>*(128k context SWA)* | 🟢 **7.93 GiB** | [unsloth/gemma-4-12B-it-qat-GGUF](https://huggingface.co/unsloth/gemma-4-12B-it-qat-GGUF) |
| **7a** | **Gemma 4 E4B (Q4_K_XL)**<br>*(Full Context 131k SWA)* | 3.93 GiB<br>`gemma-4-E4B-it-qat-UD-Q4_K_XL.gguf` | 945.6 MiB<br>`mmproj-BF16.gguf` | 94.1 MiB<br>`mtp-gemma-4-E4B-it-Q8_0.gguf` | **1.77 GiB**<br>*(131k context SWA)* | 🟢 **6.71 GiB** | [unsloth/gemma-4-E4B-it-qat-GGUF](https://huggingface.co/unsloth/gemma-4-E4B-it-qat-GGUF) |
| **7b** | **Gemma 4 E4B (Q4_K_XL)**<br>*(`-c 65536` / 64k Context)* | 3.93 GiB<br>`gemma-4-E4B-it-qat-UD-Q4_K_XL.gguf` | 945.6 MiB<br>`mmproj-BF16.gguf` | 94.1 MiB<br>`mtp-gemma-4-E4B-it-Q8_0.gguf` | **885.0 MiB**<br>*(64k context SWA)* | 🟢 **5.82 GiB** | [unsloth/gemma-4-E4B-it-qat-GGUF](https://huggingface.co/unsloth/gemma-4-E4B-it-qat-GGUF) |
| **8a** | **Gemma 4 E2B (Q4_K_XL)**<br>*(Full Context 131k SWA)* | 2.44 GiB<br>`gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf` | 941.1 MiB<br>`mmproj-BF16.gguf` | 93.3 MiB<br>`mtp-gemma-4-E2B-it-Q8_0.gguf` | **903.0 MiB**<br>*(131k context SWA)* | 🟢 **4.33 GiB** | [unsloth/gemma-4-E2B-it-qat-GGUF](https://huggingface.co/unsloth/gemma-4-E2B-it-qat-GGUF) |
| **8b** | **Gemma 4 E2B (Q4_K_XL)**<br>*(`-c 65536` / 64k Context)* | 2.44 GiB<br>`gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf` | 941.1 MiB<br>`mmproj-BF16.gguf` | 93.3 MiB<br>`mtp-gemma-4-E2B-it-Q8_0.gguf` | **451.5 MiB**<br>*(64k context SWA)* | 🟢 **3.88 GiB** | [unsloth/gemma-4-E2B-it-qat-GGUF](https://huggingface.co/unsloth/gemma-4-E2B-it-qat-GGUF) |
| **9** | **LFM 2.5 VL-3B (Q8_0)**<br>*(Vision + DSpark Draft)* | 2.68 GiB<br>`LFM2.5-VL-3B-Q8_0.gguf` | 816.1 MiB (BF16) / 556.1 MiB (Q8)<br>`mmproj-LFM2.5-VL-3B-BF16.gguf` | 540.9 MiB<br>`LFM2.5-VL-3B-DSpark-F16.gguf` | **256.0 MiB**<br>*(32k context)* | 🟢 **4.25 GiB** *(BF16 mmproj)*<br>**4.00 GiB** *(Q8 mmproj)* | [LiquidAI/LFM2.5-VL-3B-GGUF](https://huggingface.co/LiquidAI/LFM2.5-VL-3B-GGUF) |
| **10** | **LFM 2.5 VL-3B (Q4_K_M)**<br>*(Vision + DSpark Draft)* | 1.56 GiB<br>`LFM2.5-VL-3B-Q4_K_M.gguf` | 816.1 MiB (BF16) / 556.1 MiB (Q8)<br>`mmproj-LFM2.5-VL-3B-BF16.gguf` | 540.9 MiB<br>`LFM2.5-VL-3B-DSpark-F16.gguf` | **256.0 MiB**<br>*(32k context)* | 🟢 **3.13 GiB** *(BF16 mmproj)*<br>**2.88 GiB** *(Q8 mmproj)* | [LiquidAI/LFM2.5-VL-3B-GGUF](https://huggingface.co/LiquidAI/LFM2.5-VL-3B-GGUF) |
| **11a** | **LFM 2.5 1.2B Thinking**<br>*(Pure Text / LLM - Full 128k)* | 697.0 MiB<br>`LFM2.5-1.2B-Thinking-Q4_K_M.gguf` | *None (Text Only)* | *None* | **750.0 MiB**<br>*(128k context)* | 🟢 **1.41 GiB** | [LiquidAI/LFM2.5-1.2B-Thinking-GGUF](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF) |
| **11b** | **LFM 2.5 1.2B Thinking**<br>*(`-c 65536` / 64k Context)* | 697.0 MiB<br>`LFM2.5-1.2B-Thinking-Q4_K_M.gguf` | *None (Text Only)* | *None* | **375.0 MiB**<br>*(64k context)* | 🟢 **1.04 GiB** | [LiquidAI/LFM2.5-1.2B-Thinking-GGUF](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF) |
| **12a** | **LFM 2.5 1.2B Instruct**<br>*(Pure Text / LLM - Full 128k)* | 697.0 MiB<br>`LFM2.5-1.2B-Instruct-Q4_K_M.gguf` | *None (Text Only)* | *None* | **750.0 MiB**<br>*(128k context)* | 🟢 **1.41 GiB** | [LiquidAI/LFM2.5-1.2B-Instruct-GGUF](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-GGUF) |
| **12b** | **LFM 2.5 1.2B Instruct**<br>*(`-c 65536` / 64k Context)* | 697.0 MiB<br>`LFM2.5-1.2B-Instruct-Q4_K_M.gguf` | *None (Text Only)* | *None* | **375.0 MiB**<br>*(64k context)* | 🟢 **1.04 GiB** | [LiquidAI/LFM2.5-1.2B-Instruct-GGUF](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-GGUF) |
| **13** | **LFM 2.5 350M (Q8_0)**<br>*(Pure Text / LLM)* | 361.7 MiB<br>`LFM2.5-350M-Q8_0.gguf` | *None (Text Only)* | *None* | **750.0 MiB**<br>*(128k context)* | 🟢 **1.09 GiB** | [LiquidAI/LFM2.5-350M-GGUF](https://huggingface.co/LiquidAI/LFM2.5-350M-GGUF) |
| **14** | **LFM 2.5 350M (Q4_K_M)**<br>*(Pure Text / LLM)* | 218.7 MiB<br>`LFM2.5-350M-Q4_K_M.gguf` | *None (Text Only)* | *None* | **750.0 MiB**<br>*(128k context)* | 🟢 **968.7 MiB** (~0.95 GiB) | [LiquidAI/LFM2.5-350M-GGUF](https://huggingface.co/LiquidAI/LFM2.5-350M-GGUF) |
| **15** | **LFM 2.5 230M (Q4_K_M)**<br>*(Pure Text / LLM)* | 146.3 MiB<br>`LFM2.5-230M-Q4_K_M.gguf` | *None (Text Only)* | *None* | **750.0 MiB**<br>*(128k context)* | 🟢 **896.3 MiB** (~0.88 GiB) | [LiquidAI/LFM2.5-230M-GGUF](https://huggingface.co/LiquidAI/LFM2.5-230M-GGUF) |

---

## 🔗 Direct Download Links by Deployment Component

### 1. Qwen 3.8 27B
* **Base Models:**
  * Q8_K_XL: [Qwen3.8-27B-UD-Q8_K_XL.gguf](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/Qwen3.8-27B-UD-Q8_K_XL.gguf)
  * Q4_K_XL: [Qwen3.8-27B-UD-Q4_K_XL.gguf](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/Qwen3.8-27B-UD-Q4_K_XL.gguf)
  * IQ4_XS: [Qwen3.8-27B-UD-IQ4_XS.gguf](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/Qwen3.8-27B-UD-IQ4_XS.gguf)
* **Fitting `mmproj`:** [mmproj-BF16.gguf](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/mmproj-BF16.gguf) *(or [mmproj-F16.gguf](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/mmproj-F16.gguf))*
* **Fitting `mtp`:** [mtp-Qwen3.8-27B-Q4_0.gguf](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/MTP/mtp-Qwen3.8-27B-Q4_0.gguf)

### 2. Gemma 4 26B-A4B
* **Base Model:** [gemma-4-26B-A4B-it-qat-UD-Q4_K_XL.gguf](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-qat-GGUF/resolve/main/gemma-4-26B-A4B-it-qat-UD-Q4_K_XL.gguf)
* **Fitting `mmproj`:** [mmproj-BF16.gguf](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-qat-GGUF/resolve/main/mmproj-BF16.gguf) *(or [mmproj-F16.gguf](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-qat-GGUF/resolve/main/mmproj-F16.gguf))*
* **Fitting `mtp`:** [mtp-gemma-4-26B-A4B-it-Q8_0.gguf](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-qat-GGUF/resolve/main/MTP/mtp-gemma-4-26B-A4B-it-Q8_0.gguf) *(or [mtp-gemma-4-26B-A4B-it-Q4_0.gguf](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-qat-GGUF/resolve/main/MTP/mtp-gemma-4-26B-A4B-it-Q4_0.gguf))*

### 3. Gemma 4 12B (Standard 8-Bit)
* **Base Model:** [gemma-4-12b-it-UD-Q8_K_XL.gguf](https://huggingface.co/unsloth/gemma-4-12b-it-GGUF/resolve/main/gemma-4-12b-it-UD-Q8_K_XL.gguf)
* **Fitting `mmproj`:** [mmproj-BF16.gguf](https://huggingface.co/unsloth/gemma-4-12b-it-GGUF/resolve/main/mmproj-BF16.gguf)
* **Fitting `mtp`:** [mtp-gemma-4-12b-it-Q8_0.gguf](https://huggingface.co/unsloth/gemma-4-12b-it-GGUF/resolve/main/MTP/mtp-gemma-4-12b-it-Q8_0.gguf)

### 4. Gemma 4 12B (4-Bit QAT)
* **Base Model:** [gemma-4-12B-it-qat-UD-Q4_K_XL.gguf](https://huggingface.co/unsloth/gemma-4-12B-it-qat-GGUF/resolve/main/gemma-4-12B-it-qat-UD-Q4_K_XL.gguf)
* **Fitting `mmproj`:** [mmproj-BF16.gguf](https://huggingface.co/unsloth/gemma-4-12B-it-qat-GGUF/resolve/main/mmproj-BF16.gguf)
* **Fitting `mtp`:** [mtp-gemma-4-12B-it-Q8_0.gguf](https://huggingface.co/unsloth/gemma-4-12B-it-qat-GGUF/resolve/main/MTP/mtp-gemma-4-12B-it-Q8_0.gguf)

### 5. Gemma 4 E4B
* **Base Model:** [gemma-4-E4B-it-qat-UD-Q4_K_XL.gguf](https://huggingface.co/unsloth/gemma-4-E4B-it-qat-GGUF/resolve/main/gemma-4-E4B-it-qat-UD-Q4_K_XL.gguf)
* **Fitting `mmproj`:** [mmproj-BF16.gguf](https://huggingface.co/unsloth/gemma-4-E4B-it-qat-GGUF/resolve/main/mmproj-BF16.gguf)
* **Fitting `mtp`:** [mtp-gemma-4-E4B-it-Q8_0.gguf](https://huggingface.co/unsloth/gemma-4-E4B-it-qat-GGUF/resolve/main/MTP/mtp-gemma-4-E4B-it-Q8_0.gguf)

### 6. Gemma 4 E2B
* **Base Model:** [gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf](https://huggingface.co/unsloth/gemma-4-E2B-it-qat-GGUF/resolve/main/gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf)
* **Fitting `mmproj`:** [mmproj-BF16.gguf](https://huggingface.co/unsloth/gemma-4-E2B-it-qat-GGUF/resolve/main/mmproj-BF16.gguf)
* **Fitting `mtp`:** [mtp-gemma-4-E2B-it-Q8_0.gguf](https://huggingface.co/unsloth/gemma-4-E2B-it-qat-GGUF/resolve/main/MTP/mtp-gemma-4-E2B-it-Q8_0.gguf)

### 7. Liquid AI LFM 2.5 VL-3B
* **Base Models:**
  * Q8_0: [LFM2.5-VL-3B-Q8_0.gguf](https://huggingface.co/LiquidAI/LFM2.5-VL-3B-GGUF/resolve/main/LFM2.5-VL-3B-Q8_0.gguf)
  * Q4_K_M: [LFM2.5-VL-3B-Q4_K_M.gguf](https://huggingface.co/LiquidAI/LFM2.5-VL-3B-GGUF/resolve/main/LFM2.5-VL-3B-Q4_K_M.gguf)
* **Fitting `mmproj`:** [mmproj-LFM2.5-VL-3B-BF16.gguf](https://huggingface.co/LiquidAI/LFM2.5-VL-3B-GGUF/resolve/main/mmproj-LFM2.5-VL-3B-BF16.gguf) *(or [mmproj-LFM2.5-VL-3B-Q8_0.gguf](https://huggingface.co/LiquidAI/LFM2.5-VL-3B-GGUF/resolve/main/mmproj-LFM2.5-VL-3B-Q8_0.gguf))*
* **Draft Speculative Model (DSpark):** [LFM2.5-VL-3B-DSpark-F16.gguf](https://huggingface.co/LiquidAI/LFM2.5-VL-3B-DSpark-GGUF/resolve/main/LFM2.5-VL-3B-DSpark-F16.gguf)

### 8. Liquid AI LFM 2.5 Text Models
* **1.2B Thinking:** [LFM2.5-1.2B-Thinking-Q4_K_M.gguf](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Thinking-GGUF/resolve/main/LFM2.5-1.2B-Thinking-Q4_K_M.gguf)
* **1.2B Instruct:** [LFM2.5-1.2B-Instruct-Q4_K_M.gguf](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-GGUF/resolve/main/LFM2.5-1.2B-Instruct-Q4_K_M.gguf)
* **350M Q8_0:** [LFM2.5-350M-Q8_0.gguf](https://huggingface.co/LiquidAI/LFM2.5-350M-GGUF/resolve/main/LFM2.5-350M-Q8_0.gguf)
* **350M Q4_K_M:** [LFM2.5-350M-Q4_K_M.gguf](https://huggingface.co/LiquidAI/LFM2.5-350M-GGUF/resolve/main/LFM2.5-350M-Q4_K_M.gguf)
* **230M Q4_K_M:** [LFM2.5-230M-Q4_K_M.gguf](https://huggingface.co/LiquidAI/LFM2.5-230M-GGUF/resolve/main/LFM2.5-230M-Q4_K_M.gguf)
