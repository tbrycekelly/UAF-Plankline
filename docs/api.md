# Summary

 Members                        | Descriptions                                
--------------------------------|---------------------------------------------
`namespace `[`classification`](#namespaceclassification) | Classification script for UAF-Plankline
`namespace `[`cleanup`](#namespacecleanup) | Cleanup script for UAF-Plankline
`namespace `[`pull_all`](#namespacepull__all) | Image Pulling script for UAF-Plankline
`namespace `[`segmentation`](#namespacesegmentation) | Segmentation script for UAF-Plankline

# namespace `classification` 

Classification script for UAF-Plankline

Usage:
    ./classification.py -c <config.ini> -d <project directory>

License:
    MIT License

    Copyright (c) 2023 Thomas Kelly

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

## Summary

 Members                        | Descriptions                                
--------------------------------|---------------------------------------------
`public def `[`classify`](#namespaceclassification_1a058b4a55f59dd39b4354f2c7767a442f)`(tar_file)`            | Classify images contained within a TAR file.

## Members

#### `public def `[`classify`](#namespaceclassification_1a058b4a55f59dd39b4354f2c7767a442f)`(tar_file)` 

Classify images contained within a TAR file.

# namespace `cleanup` 

Cleanup script for UAF-Plankline

Usage:
    ./cleanup.py -c <config.ini> -d <project directory>

License:
    MIT License

    Copyright (c) 2023 Thomas Kelly

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

## Summary

 Members                        | Descriptions                                
--------------------------------|---------------------------------------------
`public def `[`get_size`](#namespacecleanup_1a03bc9106652f61e93711938cc3b0e2df)`(start_path)`            | 

## Members

#### `public def `[`get_size`](#namespacecleanup_1a03bc9106652f61e93711938cc3b0e2df)`(start_path)` 

# namespace `pull_all` 

Image Pulling script for UAF-Plankline

Usage:
    ./pull_all.py -d <project directory>

License:
    MIT License

    Copyright (c) 2023 Thomas Kelly

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

## Summary

 Members                        | Descriptions                                
--------------------------------|---------------------------------------------
`public def `[`directory`](#namespacepull__all_1a136a9384f9380d60a3e0e013aac446a7)`(arg)`            | 
`public def `[`csv_type`](#namespacepull__all_1af51b51486a10761a87f54271c0a4cae2)`(arg)`            | 
`public def `[`float01`](#namespacepull__all_1adb1b4a1138f4f5efce9930442b2c8f7e)`(arg)`            | 
`public def `[`add_unique_postfix`](#namespacepull__all_1a130e94888d8a223c3c49b5d25a6ac0c2)`(fn)`            | 
`public def `[`get_parser`](#namespacepull__all_1a068926d489c8f255dc0589f5845ff07b)`()`            | 
`public def `[`validate_args`](#namespacepull__all_1a4b0f6ccefc7723df59be4823b3f9a1a1)`(parser)`            | 
`public def `[`find_all_taxon`](#namespacepull__all_1af300459c0fc9fe3432fcb35f65e0e661)`(csv)`            | 
`public def `[`invalid_taxon`](#namespacepull__all_1a1a606e063a794015e72685b4d78a7328)`(parser,taxon_exist,all_taxon)`            | 
`public def `[`print_taxon`](#namespacepull__all_1aa68e059b068f53bac74b929d041137a6)`(taxon_locations)`            | 
`public def `[`find_top`](#namespacepull__all_1a3f1779a4af4380b1169dd4520418747e)`(csv,taxon_locations)`            | 
`public def `[`find_above_prob`](#namespacepull__all_1a7c02178cfb45b391367d7d7a404b75c7)`(csv,taxon_locations,probability)`            | 
`public def `[`untar`](#namespacepull__all_1a9056577087af2c734a79cd8a32850937)`(tar,out_dir)`            | 
`public def `[`build_structure`](#namespacepull__all_1ab586e829ea67d65e7dad185f04273367)`(path_array,taxon_locations)`            | 

## Members

#### `public def `[`directory`](#namespacepull__all_1a136a9384f9380d60a3e0e013aac446a7)`(arg)` 

#### `public def `[`csv_type`](#namespacepull__all_1af51b51486a10761a87f54271c0a4cae2)`(arg)` 

#### `public def `[`float01`](#namespacepull__all_1adb1b4a1138f4f5efce9930442b2c8f7e)`(arg)` 

#### `public def `[`add_unique_postfix`](#namespacepull__all_1a130e94888d8a223c3c49b5d25a6ac0c2)`(fn)` 

#### `public def `[`get_parser`](#namespacepull__all_1a068926d489c8f255dc0589f5845ff07b)`()` 

#### `public def `[`validate_args`](#namespacepull__all_1a4b0f6ccefc7723df59be4823b3f9a1a1)`(parser)` 

#### `public def `[`find_all_taxon`](#namespacepull__all_1af300459c0fc9fe3432fcb35f65e0e661)`(csv)` 

#### `public def `[`invalid_taxon`](#namespacepull__all_1a1a606e063a794015e72685b4d78a7328)`(parser,taxon_exist,all_taxon)` 

#### `public def `[`print_taxon`](#namespacepull__all_1aa68e059b068f53bac74b929d041137a6)`(taxon_locations)` 

#### `public def `[`find_top`](#namespacepull__all_1a3f1779a4af4380b1169dd4520418747e)`(csv,taxon_locations)` 

#### `public def `[`find_above_prob`](#namespacepull__all_1a7c02178cfb45b391367d7d7a404b75c7)`(csv,taxon_locations,probability)` 

#### `public def `[`untar`](#namespacepull__all_1a9056577087af2c734a79cd8a32850937)`(tar,out_dir)` 

#### `public def `[`build_structure`](#namespacepull__all_1ab586e829ea67d65e7dad185f04273367)`(path_array,taxon_locations)` 

# namespace `segmentation` 

Segmentation script for UAF-Plankline

Usage:
    ./segmentation.py -c <config.ini> -d <project directory>

License:
    MIT License

    Copyright (c) 2023 Thomas Kelly

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

## Summary

 Members                        | Descriptions                                
--------------------------------|---------------------------------------------
`public def `[`seg_ff`](#namespacesegmentation_1ad33a0fb68e616156cf9cf6fdd13f4a98)`(avi,seg_output,SNR,segment_path)`            | Formats and calls the segmentation executable
`public def `[`local_main`](#namespacesegmentation_1ae1095b4eb15bba2a5289cd64244895e0)`(avi)`            | A single threaded function that takes one avi path.
`public def `[`FixAviNames`](#namespacesegmentation_1a9da45244b61d9c55b211ca042591787f)`(avis)`            | Helper function to remove spaces in names. 

## Members

#### `public def `[`seg_ff`](#namespacesegmentation_1ad33a0fb68e616156cf9cf6fdd13f4a98)`(avi,seg_output,SNR,segment_path)` 

Formats and calls the segmentation executable

#### `public def `[`local_main`](#namespacesegmentation_1ae1095b4eb15bba2a5289cd64244895e0)`(avi)` 

A single threaded function that takes one avi path.

#### `public def `[`FixAviNames`](#namespacesegmentation_1a9da45244b61d9c55b211ca042591787f)`(avis)` 

Helper function to remove spaces in names. 
TODO: I think this is unnecessary any more.

Generated by [Moxygen](https://sourcey.com/moxygen)