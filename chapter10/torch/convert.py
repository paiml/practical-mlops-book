import torch
import torchvision

# dummy_in = torch.randn(10, 3, 224, 224)
dummy_in = torch.randn(8, 3, 200, 200)
model = torchvision.models.resnet18(pretrained=True)
#
# in_names = [ "actual_input_1" ] + [ "learned_%d" % i for i in range(16) ]
in_names = ["learned_%d" % i for i in range(16)]
out_names = ["output_1"]
#
torch.onnx.export(
    model,
    dummy_in,
    "resnet18.onnx",
    input_names=in_names,
    output_names=out_names,
    opset_version=7,
    verbose=True,
)
#

import onnx

# Load the ONNX model
model = onnx.load("resnet18.onnx")

# Check that the IR is well formed
onnx.checker.check_model(model)

# Print a human readable representation of the graph
print(onnx.helper.printable_graph(model.graph))
