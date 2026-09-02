"""
CLI Entry Point for Evaluation Subpackage
Usage: python -m perception.evaluation
"""
from perception.evaluation.evaluate_ser import evaluate_ser_on_benchmark

if __name__ == "__main__":
    evaluate_ser_on_benchmark()
