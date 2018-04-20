from compiler.PRISMParser import ModelConstructor

constructor = ModelConstructor()
mdl_fl_path = "../../prism_model/smalltest.prism"
model = constructor.parseModelFile(mdl_fl_path)
assert model.labels["failure"]() is False
model.localVars["sb_status"].setValue(0)
assert model.labels["failure"]() is True
