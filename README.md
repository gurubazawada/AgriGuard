Here’s a more concise version of your README, with placeholders left for screenshots and demo video links:

---

# 🚜 AgriGuard: Decentralized Agricultural Insurance on Algorand

<div align="center">
  <img src="https://img.shields.io/badge/Algorand-Blockchain-blue?style=for-the-badge&logo=algorand"/>
  <img src="https://img.shields.io/badge/React-Frontend-61dafb?style=for-the-badge&logo=react"/>
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi"/>
  <img src="https://img.shields.io/badge/Google%20Gemini-AI-4285f4?style=for-the-badge&logo=google"/>
</div>

## 🌟 Overview

**AgriGuard** is a decentralized insurance platform that protects farmers against agricultural risks using Algorand smart contracts, AI-driven risk assessment, and community dispute resolution.

* **Instant payouts** via smart contracts
* **Transparent AI risk assessment** with Google Gemini
* **Community governance** for disputes
* **Low-cost, global access** for farmers

## 📝 Short Summary

AgriGuard: Blockchain insurance for farmers with AI risk assessment and community governance.

## 🏗️ How It Works

* **Smart Contracts**: Automate policy creation, claim validation, and payouts.
* **AI Integration**: Google Gemini analyzes weather, crop, and market data to set premiums fairly.
* **Community Disputes**: Juror voting ensures transparent, fair resolution.
* **Algorand**: Low fees (0.001 ALGO) and 3.3s block times enable instant global access.

## 🛠️ Tech Stack

* **Frontend**: React + TypeScript, MUI, Wallet integration
* **Backend**: FastAPI, Gemini AI, AlgoKit Utils
* **Smart Contracts**: algopy (Python), ARC4 interfaces, box storage & inner transactions

## 🚀 Key Features

* One-click policy creation & AI-driven pricing
* Automated payouts on-chain
* Multi-asset premium & payout support
* Juror-based dispute resolution with audit trail
* Real-time analytics and logging

## 🎬 Demo

📹 \[**Demo Video + Audio + WalkThrough**]– https://drive.google.com/file/d/1OURWDF6LVYveYnqPvc-f33AepKs5SEwx/view?usp=sharing]

## 📸 Screenshots



* Policy Creation – <img width="2608" height="1488" alt="image" src="https://github.com/user-attachments/assets/5475f357-c346-4d01-a3af-77a6973dbf77" />

* Policy Management – <img width="2672" height="1478" alt="image" src="https://github.com/user-attachments/assets/2cfd1eb3-b662-4298-9cc4-0e5177923857" />

* Dispute Resolution – <img width="2498" height="1272" alt="image" src="https://github.com/user-attachments/assets/13f512b3-a6f8-4f8f-b1b4-bf6c90e7cdc9" />


## ⚡ Quick Start

1. Clone repo & bootstrap:

   ```bash
   git clone <repo>
   cd AgriGuard/App
   algokit project bootstrap all
   ```
2. Start LocalNet: `algokit localnet start`
3. Deploy Contracts: `algokit project deploy localnet`
4. Configure `.env` for backend & frontend
5. Run backend (`uvicorn main:app`) and frontend (`npm run dev`)

---

Would you like me to **also trim down the deep-dive technical sections** (Algorand features, architecture diagrams, security, testing) into a shorter “Additional Details” appendix at the bottom—so the core README stays hackathon-judge friendly?
