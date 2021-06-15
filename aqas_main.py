from typing import Union
from copy import deepcopy 
#I use "deepcopy" function for copying deeply nested lists and dictionaries. 
#Standard .copy() or list[:] make a shallow copy which isn't suitable for my needs


#MANUAL:
# 1. Don't use a letter "v" to stand for a propositional variable
# 2. Only use following logical constants: "v" for disjunction, "^" for conjunction, "->" for implication, "~" for negation

class AQAS:
    
    preOrSymb = "v"
    preAndSymb = "^"
    preImpSymb = "->"
    preNegSymb = "~"
    preAllSymbs = preOrSymb + preAndSymb + preImpSymb + preNegSymb
    preSqntSymb = "|-"


    orSymb = "o"
    andSymb = "a"
    impSymb = "i"
    negSymb = "n"
    sqntSymb = "|"
    formSepSymb = ","
    sepSymbs =  sqntSymb + formSepSymb
    allSymbs = orSymb + andSymb + impSymb + negSymb 
    
    ###--------------------------------PROCESS USER INPUT-----------------------------###

    def convert_string(user_question_string : str, has_spaces=True , hasLetters=True) -> str:
        s = user_question_string

        if has_spaces:
            s = s.replace(" ","")

        #check if the number of left and right brackets is the same
        brackets_sum = 0
        #max_depth = 0 ### if you want to know what's the the most nested formula's depth
        for char in s:
            if char == "(":
                brackets_sum += 1
            elif char == ")":
                brackets_sum -= 1
            #max_depth = max(max_depth,brackets_sum)
        #abort execution if the given formula has an odd number of brackets
        if brackets_sum != 0:
            raise ValueError ("<The number of left and right brackets is different>")

        #change the original sequent symbol ("|-") for the 1 character length one ("|") for ease of string manipulation
        s= s.replace(AQAS.preSqntSymb,AQAS.sqntSymb)
       
        #replaces letters standing for propositional variables for ASCII numbers. 
        #Every propositional variable is enveloped in brackets (ex. "(113)") except for standalone literals (like "r" in this set: "{...,((...)->q),r,(p^q),...}")
        if hasLetters:
            i = 0
            while i < len(s):
                if s[i].isalpha() and s[i] not in AQAS.preAllSymbs: #prevents treating logical operators as propositional variables (ex. "v" as variable when it's dysjunction)
                    tmp = str(ord(s[i])) #convert to ASCII numeric representation
                    brackets_added = False
                    if i == 0 and s[i+1] in AQAS.sepSymbs:
                        s = s.replace(s[i],tmp,1)
                    elif i == len(s)-1 and s[i-1] in AQAS.sepSymbs:
                        s = s.replace(s[i],tmp,1)
                    elif s[i-1] in AQAS.sepSymbs and s[i+1] in AQAS.sepSymbs:
                        s = s.replace(s[i],tmp,1)
                    else:
                        s = s.replace(s[i],"("+tmp+")",1)
                        brackets_added = True
                    i += len(tmp) + 2*brackets_added
                else:
                    i += 1

        #replace old operators' symbols for new 1 character length ones.
        s = s.replace(AQAS.preOrSymb,AQAS.orSymb)
        s = s.replace(AQAS.preAndSymb,AQAS.andSymb)
        s = s.replace(AQAS.preImpSymb,AQAS.impSymb)
        s = s.replace(AQAS.preNegSymb,AQAS.negSymb)

        return s

        
    ##### AWAITING IMPLMEMENTATION ######
    #This function was meant to put negated formulas in brackets (ex. "(~(p^q))") so that users doesn't have to do it themselves
    # "max _depth" variable from before might be usefull for this!
    #####################################

    #def bracket_negations(_max_depth):
    #        negIndices =[[] for i in range(_max_depth)]
    #        for index,char in enumerate(s):
    #            if char == "(":
    #                brackets_sum += 1
    #            elif char == ")":
    #                brackets_sum -= 1
    #            #find a place where negation starts
    #            if char == AQAS.negSymb and len(negIndices[brackets_sum])% 2 ==0:
    #                negIndices[brackets_sum].append(index)
    #            #find a place where negated formula ends
    #            elif char == ")" and len(negIndices[brackets_sum])% 2 ==1:
    #                negIndices[brackets_sum].append(index)


    #        #add brackets before negation sign ("n") and after the formula that is negated by that sign
    #        if any(len(x) !=0 for x in negIndices):
    #            parts = [s[i:j] for i,j in zip(negIndices, negIndices[1:]+[None])]
    #            new_s = s[:negIndices[0]]
    #            for i in range(0,len(parts),2):
    #                new_s += "(" + parts[i] + ")" + parts[i+1]
    #            s = new_s
    #            #dict = {}
    #            #alphabet = ascii_lowercase
    #            #for i in range(len(alphabet)):
    #            #    dict[alphabet[i]] = i
    #        return 0
        
    ###--------------------------------EXTRACT GAMMA AND DELTA FROM PROCESSED USER INPUT-----------------------------###

    def get_gamma_delta(processed_question : str) -> dict[str:list, str:list]:
        s = processed_question

        #split string where there is sequent symbol (ex. "|") and the where there is formula separator (ex. ",")
        s = s.split(AQAS.sqntSymb)
        s = [x.split(AQAS.formSepSymb) for x in s]
        
        gamma_delta = {"gamma":s[0], "delta":s[1]}
        for key in gamma_delta.keys():
            for i in range(len(gamma_delta[key])):
                #search for the index of a logical operator and split the formula according to it
                gamma_delta[key][i] = AQAS.find_operator_to_dissolve(gamma_delta[key][i])
                #gamma_delta[]
       
        return gamma_delta

    #This function turns formula into a list with a logical operator as the middle element and formulas next to it
    #As you can probably see we're counting brackets once again which is a bit of a waste
    def find_operator_to_dissolve(form: str)-> Union[list,None]:
        returnVal = None
        tmp_list = []
        brackets_sum = 0
        for index, char in enumerate(form):
            if char in AQAS.allSymbs and brackets_sum == 0:
                #the complicated "form" slices (ex. "form[index+2:-1]") simply: 1) takes the formula after or before the index and 2) drops outer brackets.
                #index==0 means that the operator we have found is a negation operator ("n")
                if index == 0:
                    right = AQAS.find_operator_to_dissolve(form[index+2:-1])
                    if type(right) == str:
                        returnVal = char + right
                    elif type(right) == list:
                        returnVal = [char,right]
                    
                #in other case it's either implication, disjunction or conjunction ("i", "o" or "a")
                else:
                    right = AQAS.find_operator_to_dissolve(form[index+2:-1])
                    left = AQAS.find_operator_to_dissolve(form[1:index-1])
                    returnVal = [left,char,right]
                break
            elif char == "(":
                brackets_sum += 1
            elif char == ")":
                brackets_sum -= 1

        if returnVal == None:
            returnVal = form

        return returnVal


    ###--------------------------------RULES OF INFERENCE-----------------------------###

    #Helper function used by every rule for dissolving complex formulas into simper ones
    #It helps dissolve beta and alpha formulas into subformulas. It also negates subformulas if needed
    def find_desired_form_and_process_it(form : Union[list, str], rule_type : str):
        desired_form_found = False
        
        if type(form) == str: 
            #if formula is a literal
            pass
        elif "XXX" in form:
            #used during hintikka_sets stage for preventing formulas from being dissolved
            pass
        #if formula has the following form: "[formula, logical operator, formula]"
        elif len(form) == 3: 
            if (rule_type == "BETA"):
                if form[1] == AQAS.orSymb:
                    desired_form_found = True
                    pass
                elif form[1] == AQAS.impSymb:
                    form[0] = AQAS._negate_formula(form[0])
                    desired_form_found = True
                    pass
            elif (rule_type == "ALPHA"):
                if form[1] == AQAS.andSymb:
                    desired_form_found = True
                    pass
        #if formula has the following form: "[negation, formula]" and "formula" is not a literal 
        elif form[0] == AQAS.negSymb:  
            inner_form = form[1]
            if (rule_type == "BETA"):
                if inner_form[1] == AQAS.andSymb:
                    inner_form[0] = AQAS._negate_formula(inner_form[0])
                    inner_form[2] = AQAS._negate_formula(inner_form[2])
                    desired_form_found = True
                    pass
            elif (rule_type == "ALPHA"):
                if inner_form[1] == AQAS.orSymb:
                    inner_form[0] = AQAS._negate_formula(inner_form[0])
                    inner_form[2] = AQAS._negate_formula(inner_form[2])
                    desired_form_found = True
                    pass
                elif inner_form[1] == AQAS.impSymb:
                    inner_form[2] = AQAS._negate_formula(inner_form[2])
                    desired_form_found = True
                    pass
            #in case you found what you needed change variable name
            if desired_form_found:
                form = inner_form
        return form, desired_form_found


    def _R_alpha_or_L_beta(_sequent : dict[str:list], _rule_type : str) -> tuple[list[dict,...], bool]:

        #OPTIMIZATION: instead of applying branching rules to all the formulas you can, try to find a formula to which nonbranching rule can be applied 
        #(it prevents doing the same work in many sequents)
        #Same idea in Polish: Może lepiej zasotoswać regułę beta dla pierwotnych formuł, a dla nowopowstałych formuł zasotoswać najpierw regułę alfa?

        #ADJUSTMENT TO HINTIKKA SET: 
        #branching rules (L_Beta and R_Alpha) are not appropriate for getting hintikka sets, 
        #which makes it necessary to write a separate function for getting hintikka sets (which is a waste)


        #POSSIBLE UNEXPECTED BEHAVIOURS:
        #removing and adding elements to a list that is iterated on is not a good practice, but it works here.
        #Converting "for ... in ..." loops to "while" loops is a good idea.

        key = "gamma" if _rule_type == "BETA" else "delta"

        sequents = []
        sequents.append(_sequent)
        for sqnt in sequents:
            for form in sqnt[key]:
                desired_form_found = False
                #by processing a formula we mean negating its antecedent or consequent in case of, for example, de morgan rules
                found_form, desired_form_found = AQAS.find_desired_form_and_process_it(form, _rule_type)
                #if desired formula found branch the sequent:
                # 1) delete the old formula, 
                # 2) duplicate the sequent, 
                # 3) add subformulas to sequents, 
                # 4) add new sequent to sequents' list
                if desired_form_found:
                    sqnt[key].remove(form)
                    sqnt_2 = deepcopy(sqnt)
                    sqnt[key].append(found_form[0])
                    sqnt_2[key].append(found_form[2])
                    sequents.append(sqnt_2)

        return sequents, len(sequents) != 1

    


    def _R_beta_or_L_alpha(gamma_or_delta : list, rule_type : str, is_hintikka: bool=False) -> list:
        
        #POSSIBLE UNEXPECTED BEHAVIOURS:
        #adding elements to a list that is iterated on is not a good practice, but it works here.
        #Converting "for ... in ..." loops to "while" loops is a good idea.

        for form in gamma_or_delta:
            desired_form_found = False
            found_form, desired_form_found = AQAS.find_desired_form_and_process_it(form, rule_type)
            #if desired formula found branch the sequent:
                # 1) add subformulas of the found formula to the current gamma or delta, 
                # 2) delete the old formula
                # 3*) if this function is used for making hintikka sets then a) don't delete the old formula and b) mark the old formula so it doesn't get dissolved one more time
            if desired_form_found:
                gamma_or_delta.extend([found_form[0],found_form[2]])
                if is_hintikka == False:
                    gamma_or_delta.remove(form)
                else:
                    form.append("XXX")

        return gamma_or_delta


    def _LR_double_neg(_gamma_or_delta : list) -> list:
        g_or_d = _gamma_or_delta
        for i in range(len(g_or_d)):
            #Check if the formula is double negated (=check if formula is a nested list with element[0] == negation and element[1][0] == negation)
            if type(g_or_d[i])==list:
                if g_or_d[i][0] == AQAS.negSymb and g_or_d[i][1][0] == AQAS.negSymb: 
                    g_or_d[i] = g_or_d[i][1][1]
            #If the formula is a string then check if it's prefixed with double negation ("nn")
            elif type(g_or_d[i])==str:
                if AQAS.negSymb *2 in g_or_d[i]: 
                    g_or_d[i].replace(AQAS.negSymb *2,"")
        return g_or_d

    ###--------------------------------SOCRATIC TRANSFORMATION-----------------------------###
    
    def s_transform(gamma_delta : dict[str:list]) -> list[dict[str:list],...]:
        sequents = []
        sequents.append(gamma_delta)

        while True:
            i=0
            while i < len(sequents):
                #Let's start with non-branching rules
                sequents[i]["gamma"] = AQAS._R_beta_or_L_alpha(deepcopy(sequents[i]["gamma"]),"ALPHA")
                sequents[i]["delta"] = AQAS._R_beta_or_L_alpha(deepcopy(sequents[i]["delta"]),"BETA")

                sequents[i]["gamma"] = AQAS._LR_double_neg(deepcopy(sequents[i]["gamma"]))
                sequents[i]["delta"] = AQAS._LR_double_neg(deepcopy(sequents[i]["delta"]))


                
                #Now for the branching rules...
                new_sqnts, smth_changed = AQAS._R_alpha_or_L_beta(deepcopy(sequents[i]),"BETA")
                if smth_changed :
                    sequents.remove(sequents[i])
                    sequents.extend(new_sqnts)
                

                new_sqnts, smth_changed = AQAS._R_alpha_or_L_beta(deepcopy(sequents[i]),"ALPHA")
                if smth_changed :
                    sequents.remove(sequents[i])
                    sequents.extend(new_sqnts)

                i += 1

            #Check if every formula in every sequent is a string
            if all(type(form) == str for sqnt in sequents for gamma_or_delta in sqnt.values() for form in gamma_or_delta):
                break
            else:
                continue
 
        return sequents
    
    ###--------------------------------GET OPEN SEQUENTS-----------------------------###

    def open_sequents(s_transformed_sequents : list[dict[str,list],...]) -> list:

        sequents = s_transformed_sequents
        open_sqnts = []
        for sqnt in sequents:
            for key in sqnt.keys():
                #remove duplicates
                sqnt[key] = list(set(sqnt[key]))
            is_closed  = False
            for ltrl in sqnt["gamma"]:
                # if sequent has the form: "..., p |- ..., p"
                if ltrl in sqnt["delta"]:
                    is_closed = True
                    break
                else:
                    neg_ltrl = AQAS._negate_formula(ltrl)
                    #if sequent has the form: "..., p, ~p |- ..."
                    if neg_ltrl in sqnt["gamma"]:
                        is_closed = True
                        break
            for ltrl in sqnt["delta"]:
                neg_ltrl = AQAS._negate_formula(ltrl)
                #if sequent has the form: "... |- ..., p, ~p"
                if neg_ltrl in sqnt["delta"]:
                    is_closed = True
                    break
            if is_closed == False:
                    open_sqnts.append(sqnt)

        return open_sqnts

    ###--------------------------------ABDUCTIVE RULES-----------------------------###

    #Both function create a list A of lists B. In every list B there are potential abductive hypothesis that close the sequent represented by list B 

    def abductive_rule_1(open_sqnts : list[dict[str:list],...]) -> list:
        l_negs = []
        for sqnt in open_sqnts:
            tmp = []
            for literal in sqnt["gamma"]:
                tmp.append(AQAS._negate_formula(literal))
            l_negs.append(tmp)
        return l_negs


    def abductive_rule_2(open_sqnts : list[dict[str:list],...]) -> list:
        l_imp_ks = []
        for sqnt in open_sqnts:
            tmp = []
            for l in sqnt["gamma"]: 
                for k in sqnt["delta"]: 
                    tmp.append((l, AQAS.impSymb, k)) 
            l_imp_ks.append(tmp)
        return l_imp_ks

    ###--------------------------------HINTIKKA SETS-----------------------------###

    def get_hintikka_sets(gamma_or_delta : list, isDual:bool ) -> list:

        #This function is a complete mess

        #DOES THIS FUNCTION EVEN WORK? 
        #I really don't know! It's hard to debug. 
        #What is certain is that this function creates less hintikka sets than can be seen in some of the solved AQAS problems I've seen. 
        #It means there is some problem. Probably with the merging part.

        #OPTIMIZATION: 
        #Hintikka sets should be created during socratic tranformation phase. 
        #As you examine this function you will see that it's extremely similar to what happens during socratic transformation

        #HOW TO MAKE PRETTIER: 
        #Try to reuse already existing branching rules ("_R_alpha_or_L_beta" function) 

        

        h_s = []
        h_s. append(gamma_or_delta) 

        #this variable will help us create more hintikka sets
        HS_merge_order = 0

        while True:
            sets_orig = deepcopy(h_s)
            i = 0
            while i < len(h_s):

                if isDual:
                    h_s[i] = AQAS._R_beta_or_L_alpha(deepcopy(h_s[i]),"BETA",is_hintikka = True)
                else:
                    h_s[i] = AQAS._R_beta_or_L_alpha(deepcopy(h_s[i]),"ALPHA",is_hintikka = True)
                h_s[i] = AQAS._LR_double_neg(deepcopy(h_s[i]))

                # This is the part that should be accommodated by "_R_alpha_or_L_beta" function
                for j in range(len(h_s[i])):
                    desired_form_found = False
                    if isDual:
                        form_found, desired_form_found = AQAS.find_desired_form_and_process_it(deepcopy(h_s[i][j]), "ALPHA")
                    else:
                        form_found, desired_form_found = AQAS.find_desired_form_and_process_it(deepcopy(h_s[i][j]), "BETA")
                        
                    if desired_form_found:
                        #mark which prevents already dissolved formulas from being dissolved again
                        h_s[i][j].append("XXX")
                        set2 = deepcopy(h_s[i])
                        HS_merge_order += 1
                        # "1MERGE", "2MERGE", etc. helps use generate the rest of hintikka sets later
                        h_s[i].extend([form_found[0],f"{HS_merge_order}MERGE"])
                        set2.extend([form_found[2],f"{HS_merge_order}MERGE"])
                        h_s.append(set2)
                        
                        desired_form_found = False
                i += 1
                
            if h_s != sets_orig:
                continue
            else:
                break


        #Merging part. Probably something wrong here. Good luck with debugging!
        sets_to_merge = []
        copy = deepcopy(h_s)
        while HS_merge_order > 0:
            merge_flag = f"{HS_merge_order}MERGE"
            i=0
            while i < len(copy):
                if merge_flag in copy[i]:
                    copy[i].remove(merge_flag)
                    sets_to_merge.append(copy.pop(i))
                    if len(sets_to_merge) == 2 :
                        tmp = AQAS._union_lists(sets_to_merge[0], sets_to_merge[1])
                        copy.append(tmp)
                        h_s.append(tmp)
                        sets_to_merge.clear()
                        HS_merge_order -= 1
                        break
                else:
                    i += 1 
        #Remove "1MERGE", "2MERGE", etc. labels
        for hs in h_s:
            for form in hs:
                if "MERGE" in form:
                    hs.remove(form)

        #remove duplicates from every hintikka set
        h_s = [AQAS._unique_list(x) for x in h_s]
        #remove duplicates of the same hintikka set
        h_s = AQAS._unique_list(h_s, mixed_types=True)
        return h_s

    

    ###--------------------------------CHECKING CONSISTENCY-----------------------------###
    
    def filter_inconsistencies(things_to_filter: list) -> list:
        consistent_list = []

        for ttf in things_to_filter:
            #There is an assumption here that to check consistency we only need to check if there are complementary literals (=if there are literals p and ~p)
            literals = [x for x in ttf if type(x)==str]
            literals = list(set(literals))
            for i in range(len(literals)):
                if AQAS.negSymb in literals[i]:
                    literals[i] = literals[i].replace(AQAS.negSymb,"")
            if len(set(literals)) == len(literals):
                consistent_list.append(ttf)

        return consistent_list


    ###--------------------------------RESTRICTIONS-----------------------------###

    #With these functions we only check in how many sets are restrictions met.
    #If there is some set in which restrictions are met we return True

    def consistency_restrict_1(hintikka_sets : list[list,...], l_neg : str) -> bool:
        l = AQAS._negate_formula(l_neg)
        passes = 0
        for set in hintikka_sets:
            if l not in set:
                passes += 1
        return passes > 0

    def consistency_restrict_2(hintikka_sets : list[list,...], l : str, k : str) -> bool:
        k_neg = AQAS._negate_formula(k)
        passes = 0
        for set in hintikka_sets:
            if l not in set or k_neg not in set:
                passes += 1
        return passes > 0

    def significance_restrict_1(dual_hintikka_sets : list[list,...], l_neg : str) -> bool:
        passes = 0
        for set in dual_hintikka_sets:
            if l_neg not in set:
                passes += 1
        return passes > 0

    def significance_restrict_2(dual_hintikka_sets : list[list,...],  l : str, k : str) -> bool:
        l_neg = AQAS._negate_formula(l)
        passes = 0
        for set in dual_hintikka_sets:
            if l_neg not in set or k not in set:
                passes += 1
        return  passes > 0

    ###--------------------------------GET FINAL ABDUCTIVE HYPOTHESES-----------------------------###
    def final_abd_hypotheses(l_negs_per_sqnt: list[list], l_imp_ks_per_sqnt : list[list], consistent_hintikka_sets, consistent_dual_hintikka_sets) -> list[Union[tuple,str]]:
        abductive_hypotheses=[]
        #get a list of all the potential abudctive hypotheses produced by abductive rule 1 that close every open sequent
        #in other words hypotheses which only close some open sequents are not included
        non_complex_l_negs = []
        if len(l_negs_per_sqnt) != 0:
            for l_n_0 in l_negs_per_sqnt[0]:
                is_in_all = True
                for l_negs in l_negs_per_sqnt[1:]:
                    if l_n_0 not in l_negs:
                        is_in_all = False
                        break
                if is_in_all == True:
                    non_complex_l_negs.append(l_n_0)

        #apply restrictions to potential abductive hypotheses
        #I only use .copy() here because the contents of "consistent_hitnikka_sets" variable are not modified
        #copy is probably not needed but I want to be certain that no side effects occur
        for l_neg in non_complex_l_negs:
            pass_restrictions = True
            has_passed = AQAS.consistency_restrict_1(consistent_hintikka_sets, l_neg)
            pass_restrictions = min(pass_restrictions, has_passed)
            has_passed = AQAS.significance_restrict_1(consistent_dual_hintikka_sets, l_neg)
            pass_restrictions = min(pass_restrictions, has_passed)
            if pass_restrictions == True:
                abductive_hypotheses.append(l_neg)

        #same thing as previously but for abductive rule 2
        non_complex_l_imp_ks = []
        if len(l_negs_per_sqnt) != 0:
            for l_imp_k_0 in l_imp_ks_per_sqnt[0]:
                is_in_all = True
                for l_imp_ks in l_imp_ks_per_sqnt[1:]:
                    if l_imp_k_0 not in l_imp_ks:
                        is_in_all = False
                        break
                if is_in_all == True:
                    non_complex_l_imp_ks.append(l_imp_k_0)
        #same thing as before but for potential abductive hypotheses produced by abductive rule 2
        for l_imp_k in non_complex_l_imp_ks:
            pass_restrictions = True
            has_passed = AQAS.consistency_restrict_2(consistent_hintikka_sets, l_imp_k[0], l_imp_k[2])
            pass_restrictions = min(pass_restrictions, has_passed)
            has_passed = AQAS.significance_restrict_2(consistent_dual_hintikka_sets, l_imp_k[0], l_imp_k[2])
            pass_restrictions = min(pass_restrictions, has_passed)
            if pass_restrictions == True:
                abductive_hypotheses.append(l_imp_k)

        return abductive_hypotheses


    ###--------------------------------NEGATING FORMULA-----------------------------###

    def _negate_formula(form : Union[str, list]) -> Union[str, list]:
        #if formula is a string
        if type(form) == str:
            #add AQAS.negSymb prefix to literal
            if AQAS.negSymb in form:
                #prevent double negation like "nn"
                form = form.replace(AQAS.negSymb,"")
            else:
                form = AQAS.negSymb + form
        #if formula is a list
        elif type(form) == list:
            #nest "form" in a list with AQAS.negSymb as a first element
            form = [AQAS.negSymb,form]
        else:
            raise  TypeError ("<Only strings and lists are allowed>")
        return form

    ###--------------------------------UTILITY LIST FUNCTIONS-----------------------------###

    def _union_lists(lst1 : list, lst2 : list) -> list:
            unionazied_l = deepcopy(lst1)
            tmp = [y for y in lst2 
                    if y not in unionazied_l]
            
            unionazied_l.extend(tmp)
            return unionazied_l

    def _unique_list(lst : list, mixed_types =False) -> list:
        unique_l = [] 
        
        ##non-elegant solution for lists with mixed types (ex. strings and lists)
        if mixed_types:
            tmp_list = []
            for x in lst:
                literals = sorted([form for form in x if type(form)==str])
                if literals not in tmp_list:
                    tmp_list.append(literals)
                    unique_l.append(x)

        else:
            for x in lst:
                if x not in unique_l:
                    unique_l.append(x)
        return unique_l

    ###--------------------------------CONVERT ABD. HYPOTHESES TO STRING-----------------------------###

    #This function is for the purpose of visualizing the results of AQAS - showing abductive hypotheses that pass restrictions in the form readable to every user
    def translate_to_string(abductive_hypotheses:list[Union[tuple,str]]) -> list[str]:
        pretty_hypotheses = []

        #1. change numeric representation of literals to alhpabetic represenation ("p", "q", "r", etc.)
        #2. change representation of logical operators
        for abd_h in abductive_hypotheses:
            if type(abd_h) == tuple:
                abd_h = list(abd_h)
                for i in range(len(abd_h)):
                    abd_h[i] = abd_h[i].replace(AQAS.orSymb,AQAS.preOrSymb)
                    abd_h[i] = abd_h[i].replace(AQAS.andSymb,AQAS.preAndSymb)
                    abd_h[i] = abd_h[i].replace(AQAS.impSymb,AQAS.preImpSymb)
                    if abd_h[i][0] == AQAS.negSymb:
                        abd_h[i] = abd_h[i].replace(AQAS.negSymb,AQAS.preNegSymb)
                        abd_h[i] = abd_h[i].replace(abd_h[i][1:], chr(int(abd_h[i][1:])))
                    elif abd_h[i].isnumeric():
                        abd_h[i] = abd_h[i].replace(abd_h[i], chr(int(abd_h[i])))
                abd_h = " ".join(abd_h)
            elif type(abd_h) == str:
                if abd_h[0] == AQAS.negSymb:
                        abd_h = abd_h.replace(AQAS.negSymb,AQAS.preNegSymb)
                        abd_h = abd_h.replace(abd_h[1:], chr(int(abd_h[1:])))
                elif abd_h.isnumeric():
                    abd_h = abd_h.replace(abd_h, chr(int(abd_h)))
            pretty_hypotheses.append(abd_h)


        return pretty_hypotheses

    ###--------------------------------FINAL AQAS SOLVER-----------------------------###

    def find_abductive_hypotheses(abd_question_string):
        abd_question = AQAS.convert_string(abd_question_string)
        gamma_delta = AQAS.get_gamma_delta(abd_question)
        s_transformed_sequents = AQAS.s_transform(deepcopy(gamma_delta)) ### WARNING: there might be duplicates of the same literal in a sequent 
        open_sqnts = AQAS.open_sequents(deepcopy(s_transformed_sequents)) 
        l_negs_per_sqnt = AQAS.abductive_rule_1(deepcopy(open_sqnts))
        l_imp_ks_per_sqnt = AQAS.abductive_rule_2(deepcopy(open_sqnts))
        hintikka_sets = AQAS.get_hintikka_sets(deepcopy(gamma_delta["gamma"]),isDual=False)
        dual_hintikka_sets = AQAS.get_hintikka_sets(deepcopy(gamma_delta["delta"]),isDual=True)
        consistent_hintikka_sets = AQAS.filter_inconsistencies(deepcopy(hintikka_sets))
        consistent_dual_hintikka_sets = AQAS.filter_inconsistencies(deepcopy(dual_hintikka_sets))
        abductive_hypotheses = AQAS.final_abd_hypotheses(l_negs_per_sqnt, l_imp_ks_per_sqnt, consistent_hintikka_sets, consistent_dual_hintikka_sets)

        result = AQAS.translate_to_string(abductive_hypotheses)

        return result


   
        
#################--TESTING GROUND--#################

string1 = "(~p) ^ q, q v (r ^ s) |- a -> b"
string2 = "~(pvq),~(q^(~(rvs)))|-~(a^b)"
string3 = "~(p->q), q->(~(r->s))|-avb"
string4 = "p^q, q->(~(rvs))|-avb"
string5 = "p^q, q->(~(r->s))|-~(a^b)"
string6 = "p^q, qv(r^(~s))|-a->b"
string7_complicated = "(~(~(pvp)))^(q->q), r->(qv(r^(q->r)))|-(q^q)->b"
string_wojtek = "p^q, qv(r^s)|-a->b"
string_Extended_delta = "p^q, qv(r^s) |- (~p) ^ q, q v (r ^ s)"
string_bartek = "p^q,q->(~(rvs))|-avb"
string_grzesiu1 = "(p^r)->q,((~r)->q)->p|-q"
string_grzesiu2 = "((~r)vq)->s,(~t)->(p^q),q->(~r)|-q^s"
string_grzesiu3 = "(pvq)->(sv(~r)), p->(q^(~r)),(p^q)->r,q->((~r)v(~s))|-r^q"

test_strings = []
test_strings.extend([string1,string2,string3,string4,string5,string6,string_wojtek, string_bartek, string7_complicated, string_Extended_delta, string_grzesiu1, string_grzesiu2, string_grzesiu3])

for qs in test_strings:
    print("-------",qs,"----------")
    result = AQAS.find_abductive_hypotheses(qs)
    [print(x) for x in result]


