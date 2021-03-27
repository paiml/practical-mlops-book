import sys
from coremltools.converters.onnx import convert

def main(model_path):
    basename = model_path.split('.onnx')[0]
    model = convert(model_path,  minimum_ios_deployment_target='13')
    model.short_description = "ONNX Model converted with coremltools"
    model.save(f"{basename}.mlmodel")

if __name__ == '__main__':
    main(sys.argv[-1])
