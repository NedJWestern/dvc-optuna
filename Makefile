.PHONY: dashboard

# Browse the Optuna study stored in optuna.db at http://127.0.0.1:8080
dashboard:
	uv run --with optuna-dashboard optuna-dashboard sqlite:///optuna.db
