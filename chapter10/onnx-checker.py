import sys
import onnx

def main(arguments):
    help_menu = """
    A command-line tool to quickly verify ONNX models using
    check_model()
    """

    if "--help" in arguments:
        print(help_menu)
        sys.exit(0)

    model = onnx.load(arguments[-1])
    onnx.checker.check_model(model)
    print(onnx.helper.printable_graph(model.graph))


if __name__ == '__main__':
    main(sys.argv)
