from collections import OrderedDict

meerkat_colors = {
     'del': '#FF0000',       # deletion with no insertion
     'del_ins': '#3D0000',   # deletion with insertion at breakpoint (source unknown)
     'del_inssd': '#660000', # deletion with insertion at breakpoint (from same chr, same orientation, downstream of deletion)
     'del_inssu': '#8F0000',  # deletion with insertion at breakpoint (from same chr, same orientation, upstream of deletion)
     'del_insod': '#B80000',  # deletion with insertion at breakpoint (from same chr, oppo orientation, downstream of deletion)
     'del_insou': '#D63333',  # deletion with insertion at breakpoint (from same chr, oppo orientation, upstream of deletion)
     'del_inss': '#E06666',   # deletion with insertion at breakpoint (from diff chr, same orientation)
     'del_inso': '#EB9999',   # deletion with insertion at breakpoint (from diff chr, oppo orientation)

     'del_invers': '#CC0066', # deletion with inversion at breakpoint

     'inssd': '#004C00',      # insertion (from same chr, same orientation, downstream)
     'inssu': '#006B00',      # insertion (from same chr, same orientation, upstream)
     'insod': '#008A00',      # insertion (from same chr, oppo orientation, downsteam)
     'insou': '#19A319',      # insertion (from same chr, oppo orientation, upstream)
     'inss': '#4DB84D',       # insertion (from diff chr, same orientation)
     'inso': '#80CC80',       # insertion (from diff chr, oppo orientation)

     'invers': '#FF66FF',       # inversion (with reciprocal discordant read pair cluster support)
     'tandem_dup': '#6600FF',   # tandem duplication
     'transl_inter': '#FFCC00', # inter-chromosomal translocation
     'transl_intra': '#33CCFF'  # intra-chromosomal translocation
};

meerkat_type_descriptions = {
     'del': 'Deletion with no insertion',
     'del_ins': 'Deletion with insertion at breakpoint (source unknown)',
     'del_inssd': 'Deletion with insertion at breakpoint (from same chromosome, same orientation, downstream of deletion)',
     'del_inssu': 'Deletion with insertion at breakpoint (from same chromosome, same orientation, upstream of deletion)',
     'del_insod': 'Deletion with insertion at breakpoint (from same chromosome, oppo orientation, downstream of deletion)',
     'del_insou': 'Deletion with insertion at breakpoint (from same chromosome, oppo orientation, upstream of deletion)',
     'del_inss': 'Deletion with insertion at breakpoint (from diff chromosome, same orientation)',
     'del_inso': 'Deletion with insertion at breakpoint (from diff chromosome, oppo orientation)',

     'del_invers': 'Deletion with inversion at breakpoint',

     'inssd': 'Insertion (from same chromosome, same orientation, downstream)',
     'inssu': 'Insertion (from same chromosome, same orientation, upstream)',
     'insod': 'Insertion (from same chromosome, oppo orientation, downsteam)',
     'insou': 'Insertion (from same chromosome, oppo orientation, upstream)',
     'inss': 'Insertion (from diff chromosome, same orientation)',
     'inso': 'Insertion (from diff chromosome, oppo orientation)',

     'invers': 'Inversion (with reciprocal discordant read pair cluster support)',
     'tandem_dup': 'Tandem duplication',
     'transl_inter': 'Inter-chromosomal translocation',
     'transl_intra': 'Intra-chromosomal translocation'
};

# Data taken from UCSC hg19.chrom.sizes
chromosome_sizes = { 
     'human': OrderedDict([
          ('chr1',   249250621),
          ('chr2',   243199373),
          ('chr3',   198022430),
          ('chr4',   191154276),
          ('chr5',   180915260),
          ('chr6',   171115067),
          ('chr7',   159138663),
          ('chrX',   155270560),
          ('chr8',   146364022),
          ('chr9',   141213431),
          ('chr10',  135534747),
          ('chr11',  135006516),
          ('chr12',  133851895),
          ('chr13',  115169878),
          ('chr14',  107349540),
          ('chr15',  102531392),
          ('chr16',  90354753),
          ('chr17',  81195210),
          ('chr18',  78077248),
          ('chr20',  63025520),
          ('chrY',   59373566),
          ('chr19',  59128983),
          ('chr22',  51304566),
          ('chr21',  48129895),
          ('chr6_ssto_hap7',   4928567),
          ('chr6_mcf_hap5',    4833398),
          ('chr6_cox_hap2',    4795371),
          ('chr6_mann_hap4',   4683263),
          ('chr6_apd_hap1',    4622290),
          ('chr6_qbl_hap6',    4611984),
          ('chr6_dbb_hap3',    4610396),
          ('chr17_ctg5_hap1',  1680828),
          ('chr4_ctg9_hap1',   590426),
          ('chr1_gl000192_random',  547496),
          ('chrUn_gl000225',   211173),
          ('chr4_gl000194_random',  191469),
          ('chr4_gl000193_random',  189789),
          ('chr9_gl000200_random',  187035),
          ('chrUn_gl000222',   186861),
          ('chrUn_gl000212',   186858),
          ('chr7_gl000195_random',  182896),
          ('chrUn_gl000223',   180455),
          ('chrUn_gl000224',   179693),
          ('chrUn_gl000219',   179198),
          ('chr17_gl000205_random', 174588),
          ('chrUn_gl000215',   172545),
          ('chrUn_gl000216',   172294),
          ('chrUn_gl000217',   172149),
          ('chr9_gl000199_random',  169874),
          ('chrUn_gl000211',   166566),
          ('chrUn_gl000213',   164239),
          ('chrUn_gl000220',   161802),
          ('chrUn_gl000218',   161147),
          ('chr19_gl000209_random', 159169),
          ('chrUn_gl000221',   155397),
          ('chrUn_gl000214',   137718),
          ('chrUn_gl000228',   129120),
          ('chrUn_gl000227',   128374),
          ('chr1_gl000191_random',  106433),
          ('chr19_gl000208_random', 92689),
          ('chr9_gl000198_random',  90085),
          ('chr17_gl000204_random', 81310),
          ('chrUn_gl000233',   45941),
          ('chrUn_gl000237',   45867),
          ('chrUn_gl000230',   43691),
          ('chrUn_gl000242',   43523),
          ('chrUn_gl000243',   43341),
          ('chrUn_gl000241',   42152),
          ('chrUn_gl000236',   41934),
          ('chrUn_gl000240',   41933),
          ('chr17_gl000206_random', 41001),
          ('chrUn_gl000232',   40652),
          ('chrUn_gl000234',   40531),
          ('chr11_gl000202_random', 40103),
          ('chrUn_gl000238',   39939),
          ('chrUn_gl000244',   39929),
          ('chrUn_gl000248',   39786),
          ('chr8_gl000196_random',  38914),
          ('chrUn_gl000249',   38502),
          ('chrUn_gl000246',   38154),
          ('chr17_gl000203_random', 37498),
          ('chr8_gl000197_random',  37175),
          ('chrUn_gl000245',   36651),
          ('chrUn_gl000247',   36422),
          ('chr9_gl000201_random',  36148),
          ('chrUn_gl000235',   34474),
          ('chrUn_gl000239',   33824),
          ('chr21_gl000210_random', 27682),
          ('chrUn_gl000231',   27386),
          ('chrUn_gl000229',   19913),
          ('chrM',   16571),
          ('chrUn_gl000226',   15008),
          ('chr18_gl000207_random', 4262)
     ])
}


def formatChromID(chrom_id, species='human', vcf_type='meerkat'):
     '''Converts chromosome IDs into UCSC format. Returns None if 
     unable to map the input ID to a UCSC ID.'''

     ucsc_id = None
     if vcf_type == 'meerkat':
          temp_id = chrom_id.lower()
          if 'gl' in temp_id:
               temp_id = temp_id.split('.')[0]

               for k in chromosome_sizes[species].keys():
                    if temp_id in k:
                         ucsc_id = k
                         break
          else:
               temp_id = 'chr' + chrom_id
               if temp_id in chromosome_sizes[species].keys():
                    ucsc_id = temp_id

     elif vcf_type == 'ucsc':
          if chrom_id in chromosome_sizes[species].keys():
               ucsc_id = chrom_id

     return ucsc_id




