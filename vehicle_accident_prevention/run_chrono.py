import traceback, sys
sys.path.insert(0, r"C:\Simulation System\vehicle_accident_prevention")

with open(r"C:\Simulation System\vehicle_accident_prevention\logs\run_output.txt", "w", encoding="utf-8") as log_file:
    def log_print(*args):
        text = " ".join(str(a) for a in args)
        print(text)
        log_file.write(text + "\n")
        log_file.flush()

    try:
        log_print("Starting execution...")
        import main
        main.main()
        log_print("Main execution finished successfully!")
    except Exception as e:
        log_print("Error encountered:")
        traceback.print_exc(file=log_file)
        traceback.print_exc()
