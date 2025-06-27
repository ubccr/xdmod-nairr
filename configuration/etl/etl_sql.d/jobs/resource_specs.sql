UPDATE resourcespecs SET cpu_processor_count = 2080, gpu_processor_count = 208, gpu_node_count = 52, cpu_processor_count_per_node = 40, gpu_processor_count_per_node = 4, comments = 'SDSC EXPANSE GPU Nvidia V100 GPU nodes From https://www.sdsc.edu/services/hpc/expanse/expanse_architecture.html' WHERE resource_id = 6;

UPDATE resourcespecs SET cpu_processor_count = 93184, cpu_node_count = 728, cpu_processor_count_per_node =  128, comments = 'SDSC EXPANSE AMD Rome Standard Compute Nodes and Large memory nodes From https://www.sdsc.edu/services/hpc/expanse/expanse_architecture.html' WHERE resource_id = 5;

UPDATE resourcespecs SET cpu_processor_count = 4 * 96, cpu_node_count = 4, cpu_processor_count_per_node =  96, comments = 'PSC Bridges2 EM from https://www.psc.edu/resources/bridges-2/' WHERE resource_id = 7;

UPDATE resourcespecs SET cpu_processor_count = 1888, gpu_processor_count = 360, gpu_node_count = 44, cpu_processor_count_per_node = 43, gpu_processor_count_per_node = 8, comments = 'PSC Bridges2 GPU from https://www.psc.edu/resources/bridges-2/' WHERE resource_id = 8;

UPDATE resourcespecs SET cpu_processor_count = 504 * 128, cpu_node_count = 504, cpu_processor_count_per_node =  128, comments = 'PSC Bridges2 RM from the RDR api https://rdr.xsede.org/resources/643/compute_resources/145121' WHERE resource_id = 9;

UPDATE resourcespecs SET cpu_processor_count = 11520, gpu_processor_count = 360, gpu_node_count = 90, cpu_processor_count_per_node = 128, gpu_processor_count_per_node = 4, comments = 'Jetstream2 GPU - https://docs.jetstream-cloud.org/overview/config/' WHERE resource_id = 12;

UPDATE resourcespecs SET cpu_processor_count = 1000 * 128, cpu_node_count = 1000, cpu_processor_count_per_node =  128, comments = 'Purdue Anvil https://www.rcac.purdue.edu/compute/anvil' WHERE resource_id = 13;

UPDATE resourcespecs SET cpu_processor_count = 16 * 128, gpu_processor_count = 16 * 4, gpu_node_count = 16, cpu_processor_count_per_node = 128, gpu_processor_count_per_node = 4, comments = 'Purdue Anvil GPU https://www.rcac.purdue.edu/compute/anvil' WHERE resource_id = 14;

UPDATE resourcespecs SET cpu_processor_count = 21 * 112, gpu_processor_count = 21 * 4, gpu_node_count = 20, cpu_processor_count_per_node = 112, gpu_processor_count_per_node = 4, comments = 'Purdue Anvil AI https://www.rcac.purdue.edu/compute/anvil' WHERE resource_id = 44;

UPDATE resourcespecs SET cpu_processor_count = 13568, gpu_processor_count = 848, gpu_node_count = 206, cpu_processor_count_per_node = 13568/206, gpu_processor_count_per_node = 848/206, comments = 'NCSA Delta GPU 200 x AMD 64 cores, 6 x AMD 128 cores' WHERE resource_id = 43;

UPDATE resourcespecs SET cpu_processor_count = (2488 * 128), cpu_node_count = 2488, cpu_processor_count_per_node = 128, comments = 'NSF NCAR Derecho' WHERE resource_id = 18;

UPDATE resourcespecs SET cpu_processor_count = (152 * 288), cpu_node_count = 152, cpu_processor_count_per_node = 288, gpu_processor_count = (152 * 4), gpu_node_count = 152, gpu_processor_count_per_node = 4, comments = 'NCSA DeltaAI' WHERE resource_id = 33;

UPDATE resourcespecs SET cpu_processor_count = (90 * 16), cpu_node_count = 90, cpu_processor_count_per_node = 16, gpu_processor_count = (90 * 4), gpu_node_count = 90, gpu_processor_count_per_node = 4, comments = 'Frontera GPU' WHERE resource_id = 4;

UPDATE resourcespecs SET cpu_processor_count = 560 * 128, cpu_node_count = 560, cpu_processor_count_per_node =  128, comments = 'LoneStar6' WHERE resource_id = 10;

UPDATE resourcespecs SET cpu_processor_count = 10752, cpu_node_count = 88, cpu_processor_count_per_node = (10752/88), gpu_processor_count = 260, gpu_node_count = 88, gpu_processor_count_per_node = (260/88), comments = 'Lonestar6' WHERE resource_id = 11;

UPDATE resourcespecs SET cpu_processor_count = 11888, gpu_processor_count = 34, cpu_node_count = 130, cpu_processor_count_per_node = (11888 / 130), gpu_processor_count_per_node = (34 / 130), comments = 'TAMU ACES website https://hprc.tamu.edu/kb/User-Guides/ACES/' WHERE resource_id = 3362;

UPDATE resourcespecs SET cpu_processor_count = (32 * 28), cpu_node_count = 1, cpu_processor_count_per_node =  (32 * 28), comments = 'NeoCortex CS-2' WHERE resource_id = 20;

UPDATE resourcespecs SET cpu_processor_count = (128 * 32), cpu_node_count = 32, cpu_processor_count_per_node = 128, gpu_processor_count = (32 * 8), gpu_node_count = 32, gpu_processor_count_per_node = 8, comments = 'DGX Cloud https://docs.nvidia.com/dgx/dgxa100-user-guide/introduction-to-dgxa100.html' WHERE resource_id = 26;

