Map findArgumentSchema(Map config, String argument_id) {
  def argument_groups =
    (config.argument_groups ?: []) +
    [
      arguments: config.arguments ?: []
    ]

  def schema_value = argument_groups.findResult{ gr ->
    gr.arguments.find { arg ->
      arg.name == ("--" + argument_id)
    }
  }
  return schema_value
}

Boolean checkMethodAllowed(String method, List include, List exclude) {

  // Throw an error if both include and exclude lists are provided
  if (include != null && exclude != null) {
      throw new Exception("Cannot have both include and exclude lists of method ids")
  }

  if (include) {
    return include.contains(method)
  }
  if (exclude) {
    return !exclude.contains(method)
  }

  return true
}
