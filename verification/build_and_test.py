import os
import subprocess

def get_dependencies(directory):
    v_files = []
    for root, _, files in os.walk(directory):
        if ".git" in root or "/usr" in root or "/rom/" in root:
            continue
        for file in files:
            if file.endswith('.v') and not file.startswith('tb_'):
                v_files.append(os.path.join(root, file))
    return v_files

def main():
    # Adjusted root_dir to the new src layout
    root_dir = "../src"

    # In a complex design, pulling every single .v file can cause duplicate definition issues.
    # We found earlier that passing all these files actually worked after we resolved the duplicate BUFX4 stub
    # and fixed the missing NUM_HARTS macro. However, for a clean execution, we need to correct the include paths.
    deps = get_dependencies(root_dir)
    deps_str = " ".join(deps)

    success_count = 0
    fail_count = 0

    for root, _, files in os.walk(root_dir):
        if ".git" in root or "/usr" in root or "/rom/" in root:
            continue
        for file in files:
            if file.startswith('tb_') and file.endswith('.v'):
                tb_path = os.path.join(root, file)
                print(f"--- Running Testbench: {tb_path} ---")

                # Correctly point include flags to the new src directory
                includes = "-I ../src/includes -I ../src/common"

                # We execute from the verification directory, so all outputs remain here
                compile_cmd = f"iverilog -g2012 {includes} -o sim.vvp {tb_path} {deps_str}"

                compile_result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
                if compile_result.returncode != 0:
                    print(f"Compile Failed for {tb_path}")
                    print(compile_result.stderr)
                    fail_count += 1
                    continue

                run_result = subprocess.run("vvp sim.vvp", shell=True, capture_output=True, text=True)
                if run_result.returncode != 0 or "FAIL" in run_result.stdout:
                    print(f"Sim Failed for {tb_path}")
                    print(run_result.stdout)
                    fail_count += 1
                else:
                    print(f"Pass: {tb_path}")
                    success_count += 1

    print("\n--- Summary ---")
    print(f"Passed: {success_count}")
    print(f"Failed: {fail_count}")

    if fail_count > 0:
        exit(1)

if __name__ == "__main__":
    main()
