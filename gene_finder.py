# -*- coding: utf-8 -*-
"""
YOUR HEADER COMMENT HERE

@author: Chenlin (Harry) Liu

"""

import random
from amino_acids import aa, codons, aa_table  # you may find these useful
from load import load_seq


def shuffle_string(s):
    """Shuffles the characters in the input string
        NOTE: this is a helper function, you do not
        have to modify this in any way """
    return ''.join(random.sample(s, len(s)))


# YOU WILL START YOUR IMPLEMENTATION FROM HERE DOWN ###


def get_complement(nucleotide):
    """ Returns the complementary nucleotide

        nucleotide: a nucleotide (A, C, G, or T) represented as a string
        returns: the complementary nucleotide
    >>> get_complement('A')
    'T'
    >>> get_complement('C')
    'G'
    >>> get_complement('T')
    'A'
    >>> get_complement('G')
    'C'
    """
    nu_AT_swap = nucleotide.replace('A', 'K').replace('T', 'A').replace('K', 'T')
    nu_CG_swap = nu_AT_swap.replace('C', 'S').replace('G', 'C').replace('S', 'G')

    return nu_CG_swap


def get_reverse_complement(dna):
    """ Computes the reverse complementary sequence of DNA for the specfied DNA
        sequence

        dna: a DNA sequence represented as a string
        returns: the reverse complementary DNA sequence represented as a string
    >>> get_reverse_complement("ATGCCCGCTTT")
    'AAAGCGGGCAT'
    >>> get_reverse_complement("CCGCGTTCA")
    'TGAACGCGG'
    """
    dna_complement = get_complement(dna)
    dna_reverse_complement = dna_complement[::-1]  # reverse the complement

    return dna_reverse_complement


def rest_of_ORF(dna):
    """ Takes a DNA sequence that is assumed to begin with a start
        codon and returns the sequence up to but not including the
        first in frame stop codon.  If there is no in frame stop codon,
        returns the whole string.

        dna: a DNA sequence
        returns: the open reading frame represented as a string
    >>> rest_of_ORF("ATGTGAA")
    'ATG'
    >>> rest_of_ORF("ATGAGATAGG")
    'ATGAGA'
"""

    i = 0
    while i <= len(dna) - 3:
        if dna[i:i + 3] == "TAG" or dna[i:i + 3] == "TAA" or dna[i:i + 3] == "TGA":
            return dna[0:i]
        else:
            i = i + 3
    return dna


def find_all_ORFs_oneframe(dna):
    """ Finds all non-nested open reading frames in the given DNA
        sequence and returns them as a list.  This function should
        only find ORFs that are in the default frame of the sequence
        (i.e. they start on indices that are multiples of 3).
        By non-nested we mean that if an ORF occurs entirely within
        another ORF, it should not be included in the returned list of ORFs.

        dna: a DNA sequence
        returns: a list of non-nested ORFs
    >>> find_all_ORFs_oneframe("ATGCATGAATGTAGATAGATGTGCCC")
    ['ATGCATGAATGTAGA', 'ATGTGCCC']
    """

    final_list = []
    i = 0
    while i <= len(dna) - 3:
        codon = dna[i:i + 3]
        if codon == "ATG":
            orf = rest_of_ORF(dna[i:])
            final_list.append(orf)
            i = i + len(orf) + 3
        else:
            i = i + 3
    return final_list


def find_all_ORFs(dna):
    """ Finds all non-nested open reading frames in the given DNA sequence in
        all 3 possible frames and returns them as a list.  By non-nested we
        mean that if an ORF occurs entirely within another ORF and they are
        both in the same frame, it should not be included in the returned list
        of ORFs.

        dna: a DNA sequence
        returns: a list of non-nested ORFs

    >>> find_all_ORFs("ATGCATGAATGTAG")
    ['ATGCATGAATGTAG', 'ATGAATGTAG', 'ATG']
    """

    final_list = []
    for i in range(0,3):
        orf = find_all_ORFs_oneframe(dna[i:])
        final_list.extend(orf)
    return final_list


def find_all_ORFs_both_strands(dna):
    """ Finds all non-nested open reading frames in the given DNA sequence on both
        strands.

        dna: a DNA sequence
        returns: a list of non-nested ORFs
    >>> find_all_ORFs_both_strands("ATGCGAATGTAGCATCAAA")
    ['ATGCGAATG', 'ATGCTACATTCGCAT']
    """

    all_orf_1 = find_all_ORFs(dna)
    strand_dna_1 = get_reverse_complement(dna)
    all_orf_2 = find_all_ORFs(strand_dna_1)
    return list(all_orf_1 + all_orf_2)


##################################################### End of Week1 #####################################################

def longest_ORF(dna):
    """ Finds the longest ORF on both strands of the specified DNA and returns it
        as a string
    >>> longest_ORF("ATGCGAATGTAGCATCAAA")
    'ATGCTACATTCGCAT'
    """
    longest_orf = find_all_ORFs_both_strands(dna)
    a = 0
    s = ''
    for i in longest_orf:
        if len(i) > a:
            a = len(i)
            s = i
    return s


def longest_ORF_noncoding(dna, num_trials):
    """ Computes the maximum length of the longest ORF over num_trials shuffles
        of the specfied DNA sequence

        dna: a DNA sequence
        num_trials: the number of random shuffles
        returns: the maximum length longest ORF """
    s = 0
    longest_orf_1 = ""
    p = 0
    for i in range(0, num_trials):
        shuffled_dna = shuffle_string(dna)
        longest_orf_1 = longest_ORF(shuffled_dna)
        if len(longest_orf_1) > p:
            p = len(longest_orf_1)

    return p


def coding_strand_to_AA(dna):
    """ Computes the Protein encoded by a sequence of DNA.  This function
        does not check for start and stop codons (it assumes that the input
        DNA sequence represents an protein coding region).

        dna: a DNA sequence represented as a string
        returns: a string containing the sequence of amino acids encoded by the
                 the input DNA fragment

        >>> coding_strand_to_AA("ATGCGA")
        'MR'
        >>> coding_strand_to_AA("ATGCCCGCTTT")
        'MPA'
    """

    m = []
    s = 0
    while s <= len(dna) - 3:
        m.append(aa_table[dna[s:s + 3]])
        s = s + 3
    k = ''
    k = k.join(m)
    return k


def gene_finder(dna):
    """ Returns the amino acid sequences that are likely coded by the specified dna

        dna: a DNA sequence
        returns: a list of all amino acid sequences coded by the sequence dna.
    """
    ac = []
    threshold = longest_ORF_noncoding(dna, 1500)
    dna_long = find_all_ORFs_both_strands(dna)
    for i in dna_long:
        if len(i) > threshold:
            ac.append(coding_strand_to_AA(i))

    return ac


if __name__ == "__main__":
    import doctest

    print(gene_finder(dna=load_seq("./data/X73525.fa")))
    doctest.testmod(verbose=True)
