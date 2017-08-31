import json
import requests
import csv
import xmltodict
import pprint
from collections import OrderedDict

def extract_remote(url):
    return extract(requests.get(url).content)


def handle_candidate(root):
    candidate = {}
    candidate['id'] = root['CandidateIdentifier']['@Id']
    candidate['name'] = root['CandidateIdentifier']['CandidateName']
    if type(root['Incumbent']) == OrderedDict:
        candidate['incumbent'] = root['Incumbent']['@Notional']
    else:
        candidate['incumbent'] = root['Incumbent']
    votes = root['Votes']
    candidate['votes'] = {k.strip('@').lower(): v for k, v in votes.items() 
                          if not k in ['#text', '@MatchedHistoric']}
    try:
        candidate['affiliation'] = {k.strip('@').lower(): v for k, v in root['AffiliationIdentifier'].items()}
    except Exception as e:
        candidate['affiliation'] = {'registeredname': 'independent', 'id': -1, 'shortcode': 'IND'}
    return candidate

def handle_election_meta(root):
    pass

def handle_simple_candidate(root):
    return {k.strip('@').lower(): v for k, v in root.items()}
def handle_group(root):
    # Ignore ticket votes, unapportioned, individual candidates
    group = {k.strip('@').lower(): v for k, v in root['GroupIdentifier'].items()}
    group['candidates'] = list(map(handle_candidate, root['Candidate']))
    group['votes'] = {k.strip('@').lower(): v for k, v in root['GroupVotes']['Votes'].items()
                    if not k in ['#text', '@QuotaProportion']}
    return group

def extract_election(election):
    cat = election['ElectionIdentifier']['ElectionCategory']
    if cat == "ByElection":
        if len(election.keys()) == 2:
            cat = next(filter(lambda x: x != 'ElectionIdentifier', election.keys()))
        # no known multicameral system bunches byelections involving
        # both houses
    contests = election[cat]['Contests']['Contest']
    if type(contests) == OrderedDict:
        # individual contest
        contests = [contests]
    contest_summaries = list(map(handle_contest, contests))
    return {"contests": contest_summaries, "category": cat}
def handle_contest(contest):    
    ungrouped_candidates = []
    if 'Candidate' in contest['FirstPreferences'].keys():
        grouped_candidates = []
        ungrouped_candidates = contest['FirstPreferences']['Candidate']
    else:
        if 'UngroupedCandidate' in contest['FirstPreferences'].keys():
            ungrouped_candidates = contest['FirstPreferences']['UngroupedCandidate']
        if type(ungrouped_candidates) == OrderedDict:
            # happen to have only one record
            ungrouped_candidates = [ungrouped_candidates]
        grouped_candidates = contest['FirstPreferences']['Group']
    fp_groups = list(map(handle_group, grouped_candidates))
    fp_candidates_ugr = list(map(handle_candidate, ungrouped_candidates))
    return {"ungrouped_candidates": fp_candidates_ugr,
            "grouped_candidates": fp_groups}
def extract(xmlstring):
    namespaces = {
        "http://www.aec.gov.au/xml/schema/mediafeed": None,
        "urn:oasis:names:tc:evs:schema:eml": None
    }
    data = xmltodict.parse(xmlstring, process_namespaces=True, namespaces=namespaces)
    elections = data['MediaFeed']['Results']['Election']
    if type(elections) == OrderedDict:
        elections = [elections]
    processed_elections = list(map(extract_election, elections))
    with open('election.json', 'w') as f:
        json.dump(processed_elections, f)
        

if __name__ == "__main__":
    with open('./senate.xml', 'r') as f:
        extract(f.read())