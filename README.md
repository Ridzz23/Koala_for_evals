Koala Benchmark Evaluation for PEPPER
======================================

This evaluation aims to test expressiveness and accuracy of PEPPER.  

How to recreate the results:

- Build Docker (same docker build as the official Koala Benchmark except we have included few more files):
``docker run -it --rm \
  --platform linux/amd64 \
  --cap-add=SYS_PTRACE --cap-add=NET_RAW --cap-add=NET_ADMIN \
  --security-opt seccomp=unconfined \
  -v "$(pwd):/koala_evals" \
  ghcr.io/binpash/benchmarks:latest bash
`` 
- Build CPython to produce the ./python.exe executable
- navigate to the benchmark folder you want to run within the ``Koala`` parent folder. For instance if we go to the ``unixfun`` folder then:
  - first run ``./install.sh`` to install any dependencies
  - then ``./fetch.sh --small`` to fetch the input dataset
  - then first run ``./execute.sh --small`` to produce the original shell script results
  - then run ``./execute_pepper.sh --small`` to produce the equivalent PEPPER script results
  - Finally run the script ``./validate_pepper.sh`` that checks if the contents of the shell and pepper outputs of each file are the same (after striping leading and trailing whitepsaces and newlines).
 
