import os
import pandas as pd
import requests
import yfinance as yf

# Récupération sécurisée des secrets configurés dans GitHub
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TICKERS = [
    "ABVX.PA",
    "AC.PA",
    "ADP.PA",
    "AI.PA",
    "AIR.PA",
    "AKE.PA",
    "ALO.PA",
    "AM.PA",
    "AMUN.PA",
    "ANTIN.PA",
    "ARG.PA",
    "ATO.PA",
    "AXA.PA",
    "AYV.PA",
    "BELI.PA",
    "BIM.PA",
    "BN.PA",
    "BNP.PA",
    "BOL.PA",
    "BOUY.PA",
    "CAP.PA",
    "CA.PA",
    "COV.PA",
    "ACA.PA",
    "DEC.PA",
    "DG.PA",
    "DSY.PA",
    "EDEN.PA",
    "EDF.PA",
    "ELIS.PA",
    "ELIOR.PA",
    "EL.PA",
    "ENGI.PA",
    "EN.PA",
    "ENX.PA",
    "EO.PA",
    "ERA.PA",
    "ERF.PA",
    "ES.PA",
    "ETL.PA",
    "EURA.PA",
    "EXG.PA",
    "FNAC.PA",
    "FR.PA",
    "GFC.PA",
    "GET.PA",
    "GLE.PA",
    "GNFT.PA",
    "GTT.PA",
    "HO.PA",
    "ICAD.PA",
    "IPS.PA",
    "ITP.PA",
    "KER.PA",
    "LI.PA",
    "LR.PA",
    "MC.PA",
    "MF.PA",
    "ML.PA",
    "MT.PA",
    "NXI.PA",
    "ORA.PA",
    "OR.PA",
    "OVH.PA",
    "PUB.PA",
    "RCO.PA",
    "RMS.PA",
    "RNO.PA",
    "RUI.PA",
    "RXL.PA",
    "SAF.PA",
    "SAN.PA",
    "SASY.PA",
    "SCR.PA",
    "SGO.PA",
    "SK.PA",
    "SOI.PA",
    "SOLB.PA",
    "SOP.PA",
    "SPIE.PA",
    "STMPA.PA",
    "SU.PA",
    "SW.PA",
    "TEP.PA",
    "TFI.PA",
    "TTE.PA",
    "UBI.PA",
    "URW.PA",
    "VCT.PA",
    "VIE.PA",
    "VIV.PA",
    "VU.PA",
    "WLN.PA",
    "XFAB.PA",
]


def send_telegram_message(message):
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}

  try:
    response = requests.post(url, data=payload, timeout=10)
    response.raise_for_status()
  except Exception as e:
    print(f"Erreur envoi Telegram : {e}")


def run_screener():
  signals = []

  for ticker in TICKERS:
    try:
      df = yf.download(
          ticker, period="3mo", interval="1d", auto_adjust=True, progress=False
      )

      if df is None or len(df) < 22:
        continue

      if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

      df["Donchian_High_20"] = df["High"].shift(1).rolling(20).max()
      df["Vol_SMA_20"] = df["Volume"].shift(1).rolling(20).mean()

      last_close = float(df["Close"].iloc[-1])
      last_high_20 = float(df["Donchian_High_20"].iloc[-1])
      last_vol = float(df["Volume"].iloc[-1])
      last_vol_sma = float(df["Vol_SMA_20"].iloc[-1])

      if pd.isna(last_high_20) or pd.isna(last_vol_sma):
        continue

      if last_close > last_high_20 and last_vol > last_vol_sma:
        signals.append({
            "ticker": ticker.replace(".PA", ""),
            "close": round(last_close, 2),
            "resistance": round(last_high_20, 2),
            "stop_loss": round(last_close * 0.96, 2),
            "take_profit": round(last_close * 1.10, 2),
        })

    except Exception as e:
      print(f"Erreur sur {ticker} : {e}")

  if not signals:
    print("Aucun signal détecté ce jour.")
    return

  lignes = []

  for s in signals:
    lignes.append(
        f"<b>{s['ticker']}</b>\n"
        f"Cours : {s['close']} €\n"
        f"Plus haut 20j : {s['resistance']} €\n"
        f"Stop -4% : {s['stop_loss']} €\n"
        f"Objectif +10% : {s['take_profit']} €\n"
    )

  message = (
      "<b>SIGNALS D'ACHAT SBF 120</b>\n\n"
      + "\n".join(lignes)
      + "\nSortie maximale : 15 séances"
  )

  send_telegram_message(message)
  print(f"{len(signals)} signal(s) envoyé(s).")


if __name__ == "__main__":
  run_screener()
