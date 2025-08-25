# Format euro
def fmt_eur(x):
    try:
        return f"€{int(round(float(x))):,}".replace(",", " ")
    except Exception:
        return x

# Format integer
def fmt_int(x):
    try:
        return f"{int(round(float(x))):,}".replace(",", " ")
    except Exception:
        return x