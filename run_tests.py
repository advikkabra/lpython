#!/usr/bin/env python

import argparse
import hashlib
import os
import subprocess

import toml

from compiler_tester.tester import (RunException, run, run_test, color,
    style, print_check, fg)

def main():
    parser = argparse.ArgumentParser(description="LFortran Test Suite")
    parser.add_argument("-u", "--update", action="store_true",
            help="update all reference results")
    parser.add_argument("-l", "--list", action="store_true",
            help="list all tests")
    parser.add_argument("-t", metavar="TEST",
            help="Run a specific test")
    parser.add_argument("-v", "--verbose", action="store_true",
            help="increase test verbosity")
    parser.add_argument("--no-llvm", action="store_true",
            help="Skip LLVM tests")
    args = parser.parse_args()
    update_reference = args.update
    list_tests = args.list
    specific_test = args.t
    verbose = args.verbose
    no_llvm = args.no_llvm

    # So that the tests find the `lfortran` executable
    os.environ["PATH"] = os.path.join(os.getcwd(), "src", "bin") \
            + os.pathsep + os.environ["PATH"]

    d = toml.load(open("tests/tests.toml"))
    for test in d["test"]:
        filename = test["filename"]
        if specific_test and filename != specific_test:
            continue
        tokens = test.get("tokens", False)
        ast = test.get("ast", False)
        ast_indent = test.get("ast_indent", False)
        ast_f90 = test.get("ast_f90", False)
        ast_cpp = test.get("ast_cpp", False)
        ast_cpp_hip = test.get("ast_cpp_hip", False)
        ast_openmp = test.get("ast_openmp", False)
        asr = test.get("asr", False)
        asr_preprocess = test.get("asr_preprocess", False)
        asr_indent = test.get("asr_indent", False)
        mod_to_asr = test.get("mod_to_asr", False)
        llvm = test.get("llvm", False)
        cpp = test.get("cpp", False)
        obj = test.get("obj", False)
        x86 = test.get("x86", False)
        bin_ = test.get("bin", False)
        pass_ = test.get("pass", None)
        if pass_ and pass_ not in ["do_loops", "global_stmts"]:
            raise Exception("Unknown pass: %s" % pass_)

        print(color(style.bold)+"TEST:"+color(style.reset), filename)

        extra_args = "--no-error-banner"

        if tokens:
            run_test("tokens", "lfortran --no-color --show-tokens {infile} -o {outfile}",
                    filename, update_reference, extra_args)

        if ast:
            run_test("ast", "lpython --show-ast --no-color {infile} -o {outfile}",
                        filename, update_reference, extra_args)

        if asr:
            run_test("asr", "lpython --show-asr --no-color {infile} -o {outfile}",
                    filename, update_reference, extra_args)

        if asr_preprocess:
            run_test("asr_preprocess", "lfortran --cpp --show-asr --no-color {infile} -o {outfile}",
                    filename, update_reference, extra_args)

        if asr_indent:
            run_test("asr_indent", "lfortran --show-asr --indent --no-color {infile} -o {outfile}",
                filename, update_reference, extra_args)

        if mod_to_asr:
            run_test("mod_to_asr", "lfortran mod --show-asr --no-color {infile}",
                    filename, update_reference)

        if pass_ == "do_loops":
            run_test("pass_do_loops", "lfortran --pass=do_loops --show-asr --no-color {infile} -o {outfile}",
                    filename, update_reference, extra_args)

        if pass_ == "global_stmts":
            run_test("pass_global_stmts", "lfortran --pass=global_stmts --show-asr --no-color {infile} -o {outfile}",
                    filename, update_reference, extra_args)

        if llvm:
            if no_llvm:
                print("    * llvm   SKIPPED as requested")
            else:
                run_test("llvm", "lpython --no-color --show-llvm {infile} -o {outfile}",
                        filename, update_reference, extra_args)

        if cpp:
            run_test("cpp", "lfortran --no-color --show-cpp {infile}",
                    filename, update_reference, extra_args)

        if obj:
            if no_llvm:
                print("    * obj    SKIPPED as requested")
            else:
                run_test("obj", "lfortran --no-color -c {infile} -o output.o",
                        filename, update_reference, extra_args)

        if x86:
            run_test("x86", "lfortran --no-color --backend=x86 {infile} -o output",
                    filename, update_reference, extra_args)

        if bin_:
            run_test("bin", "lfortran --no-color {infile} -o {outfile}",
                    filename, update_reference, extra_args)


        print()

    if list_tests:
        return

    if update_reference:
        print("Reference tests updated.")
    else:
        print("%sTESTS PASSED%s" % (color(fg.green)+color(style.bold),
            color(fg.reset)+color(style.reset)))

if __name__ == "__main__":
    main()
