"""Helper functions related to subsetting AnnData objects based on the file format 
specifications in the .config.vsh.yaml and slot mapping overrides."""

def read_config_slots_info(config_file, slot_mapping = {}):
    """Read the .config.vsh.yaml to find out which output slots need to be copied to which output file.
    
    Arguments:
    config_file -- Path to the .config.vsh.yaml file (required).
    slot_mapping -- Which slots to retain. Must be a dictionary whose keys are the names 
      of the AnnData structs, and values is another dictionary with destination value
      names as keys and source value names as values.
      Example of slot_mapping: 
        ```
        slot_mapping = {
          "layers": {
            "counts": par["layer_counts"],
          },
          "obs": {
            "cell_type": par["obs_cell_type"],
            "batch": par["obs_batch"],
          }
        }
        ```
    """
    import openproblems

    # read output spec from yaml
    config = openproblems.project.read_viash_config(config_file)

    output_struct_slots = {}

    # fetch info on which slots should be copied to which file
    for arg in config["all_arguments"]:
        # argument is an output file with a slot specification
        arg_info = arg.get("info") or {}
        arg_format = arg_info.get("format") or {}
        if arg["type"] == "file" and arg_format:
            # just in case it's missing
            assert arg_format.get("type"), f"Missing type in .info.format for {arg['name']}"
            output_struct_slots[arg["clean_name"]] = arg_format

    return output_struct_slots

# create new anndata objects according to api spec
def subset_anndata(adata, format):
    """Create new anndata object according to slot info specifications.
    
    Arguments:
    adata -- An AnnData object to subset (required)
    format -- Which slots to retain, typically one of the items in the output of read_config_slots_info.
      Must be a dictionary whose keys are the names of the AnnData structs, and values is another 
      dictionary with destination value names as keys and source value names as values. 
      """
    import pandas as pd
    import anndata as ad

    assert isinstance(adata, ad.AnnData), "adata must be an AnnData object"
    assert format.get("type") == "h5ad", "format must be a h5ad type"

    structs = ["layers", "obs", "var", "uns", "obsp", "obsm", "varp", "varm"]
    kwargs = {}

    for struct in structs:
        slot_mapping = format.get(struct, {})
        data = {dest : getattr(adata, struct)[src] for (dest, src) in slot_mapping.items()}
        if len(data) > 0:
            if struct in ['obs', 'var']:
                data = pd.concat(data, axis=1)
            kwargs[struct] = data
        elif struct in ['obs', 'var']:
            # if no columns need to be copied, we still need an 'obs' and a 'var' 
            # to help determine the shape of the adata
            kwargs[struct] = getattr(adata, struct).iloc[:,[]]

    return ad.AnnData(**kwargs)
