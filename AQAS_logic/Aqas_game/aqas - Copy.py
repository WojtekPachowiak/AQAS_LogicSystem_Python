from string import ascii_lowercase
from typing import Union

class AQAS_Solver:
    #TO_DO: sprawdzić jak zrobić typ: lista tupli
    #TO_DO: tuple czy słownik???
    type_sqnt = list[dict[str:list,str:list],...]


    def convert_string(question_s : str, has_spaces=True, hasLetters=True) -> str:
        s = question_s

        if has_spaces:
            s = s.replace(" ","")

        if hasLetters:
            for char in s:
              if char.isalpha() and char != "v":    #TO_DO: a co jak ktoś używa litery "v" dla oznaczenia zmiennej?
                  s = s.replace(char,str(ord(char)))

        s = s.replace("v","or")
        s = s.replace("^","and")
        s = s.replace("->","imp")
        s = s.replace("~","neg")
        #dict = {}
        #alphabet = ascii_lowercase
        #for i in range(len(alphabet)):
        #    dict[alphabet[i]] = i
        return s

        
        #"^", "v", "->", "<-"
        




    def get_gamma_delta(question : str) -> tuple[list, list]:
        s = s.split("|-")
        s = [x.split(",") for x in s]
        gamma = s[0]
        delta = s[1]
        return (gamma, delta)


    def _L_alpha(gamma : list) -> list:
        #TODO: zrób, żeby for in loop nie skończył się dopóki wszystkie formuły (wraz z nowo dodanymi) nie zostaną sprawdzone. 
        #(Obecnie jest możliwe, że ostatnia formuła (gamma[-1]) jest usuwana, nowa dodana (gamma[-1]) i ta nowa nie zostaje spradzona)
        for form in gamma:
            if type(form) == str: 
                #jeśli formuła jest literałem
                pass
            elif len(form) == 3: 
                #jeśli formuła ma postać: "formuła operator formuła"
                if form[1] == "and":
                    gamma.extend([form[0],form[2]])
                    gamma.remove(form)
                    continue
            elif form[0] == "neg" and type(form[1]) == list:  
                #jeśli formuła ma postać: "negacja formuła" (gdzie formuła nie jest literałem) 
                # "type(form[1]) == list" jest redundantne TODO: sprawdzić czy będę potrzebował tego warunku
                if "or" in form[1]:
                    form[0] = _negate_formula(form[0])
                    form[2] = _negate_formula(form[2])
                    gamma.extend([form[0],form[2]])
                    gamma.remove(form)
                elif "imp" in form[1]:
                    form[2] = _negate_formula(form[2])
                    gamma.extend([form[0],form[2]])
                    gamma.remove(form) 

        # znajdź listę, która zawiera formułę alfa
        # weź 0 i 2 (trzeci) element 
        # przetransformuj 0 i 2  
        # umieść 0 i 2 w liście nadrzędnej. 
        # element 1 (drugi) zostaw 
        # usuń pierwotną listę
        return gamma

    #def _branch_sequents(sequent, form1, form2, negate_form_1, negate_form_2):
    #    if negate_form_1:
    #        form1 = _negate_formula(form1)
    #    if negate_form_2:
    #        form2 = _negate_formula(form2)
        
    #    return sequent,form1,form2


    def _L_beta(gamma : list) -> Union[list, list[list]]:
        #TODO: zrób funkcje, która robi nową gammę, dodaje ją do sequents, odpowiednio neguje formuły (arguemnty boolowskie)
        #TODO: czy warto maksymalnie stosować reguły dla beta (stosować nawet na nowopowstałych formułach, które mogą być alfa)? 
        #Może lepiej zasotoswać regułę beta dla pierwotnych formuł, a dla nowopowstałych formuł zasotoswać najpierw regułę alfa?

        sequents = []
        sequents.append(gamma)
        for sqnt in sequents:
            for form in sqnt:
                if type(form) == str: 
                    #jeśli formuła jest literałem
                    pass
                elif len(form) == 3: 
                    #jeśli formuła ma postać: "formuła operator formuła"
                    if form[1] == "or":
                        sqnt.remove(form)
                        sqnt_2 = sqnt[:]
                        sqnt.append(form[0])
                        sqnt_2.append(form[2])
                        sequents.append(sqnt_2)
                        continue
                    elif form[1] == "imp":
                        sqnt.remove(form)
                        sqnt_2 = sqnt[:]
                        form[0] = _negate_formula(form[0])
                        sqnt.append(form[0])
                        sqnt_2.append(form[2])
                        sequents.append(sqnt_2)
                        continue
                elif form[0] == "neg" and type(form[1]) == list:  
                    #jeśli formuła ma postać: "negacja formuła" (gdzie formuła nie jest literałem) 
                    # "type(form[1]) == list" jest redundantne TODO: sprawdzić czy będę potrzebował tego warunku
                    if "and" in form[1]:
                        sqnt.remove(form)
                        sqnt_2 = sqnt[:]
                        form[0] = _negate_formula(form[0])
                        form[2] = _negate_formula(form[2])
                        sqnt.append(form[0])
                        sqnt_2.append(form[2])
                        sequents.append(sqnt_2)
                        continue
             
        #> znajdź listę, która zawiera formułę beta 
        #> weź 0 i 2 (trzeci) element 
        #> przetransformuj 0 i 2 
        #> zduplikuj gammę
        #> umieść 0 i 2 w osobnych gammach
        #> element 1 (drugi) zostaw i usuń pierwotną listę
        return sequents


    #def _L_double_neg(gamma : list) -> list:
    #    #> znajdź formułę podwójnie zanegowaną
    #    #> usuń oba znaki negacji
    #    return gamma

    def _R_alpha(delta : list) -> list:
        #> znajdź listę, która zawiera formułę beta 
        #> weź 0 i 2 (trzeci) element 
        #> przetransformuj 0 i 2 
        #> zduplikuj deltę
        #> umieść 0 i 2 w osobnych deltach
        #> element 1 (drugi) zostaw i usuń pierwotną listę
        return delta

    def _R_beta(delta : list) -> list:
        # znajdź listę, która zawiera formułę beta
        # weź 0 i 2 (trzeci) element
        # przetransformuj 0 i 2 
        # umieść je w liście nadrzędnej
        # element 1 (drugi) zostaw. 
        # usuń pierwotną listę.
        return delta

    def _LR_double_neg(gamma_or_delta : list) -> list:
        for literal in gamma_or_delta:
            if "negneg" in literal: 
                literal.replace("negneg","") 
        return gamma_or_delta

    
    def s_transform(gamma_delta : dict[str:list, str:list]) -> type_sqnt:
        sequents = []
        sequents.append(gamma_delta)


        gamma = gamma_delta["gamma"]
        delta = gamma_delta["delta"]

        #TODO: zamiast sprawdzania czy smth_changed == False może lepiej byłoby zrobić funkcje, która sprawdza czy w każdym sekwencie zostały same literały?
        while True:
            smth_changed = False
            for sqnt in sequents:
                for form in sqnt:

                    new_form = _L_alpha(form)
                    if len(new_form) != len(form):
                        smth_changed = True
                    form = new_form

                    new_form = _LR_double_neg(form)
                    if new_form != form:
                        smth_changed = True
                    form = new_form

                    new_sqnts = _L_beta(form)
                    if len(new_sqnts) > 1:
                        sequents.extend(new_sqnts)
                        smth_changed = True
        
            if smth_changed == False:
                break

        return sequents
    
    

    def abductive_rule_1(sequents : type_sqnt) -> list:
        pre_abductive_hypotheses_1 = []
        for sqnt in sequents:
            for literal in sqnt["gamma"]:
                pre_abductive_hypotheses_1.append(_negate_formula(literal))
        return pre_abductive_hypotheses_1


    def abductive_rule_2(sequents : type_sqnt) -> list:
        pre_abductive_hypotheses_2 = []
        for sqnt in sequents:
            for g_literal in sqnt["gamma"]: 
                for d_literal in sqnt["delta"]: 
                    pre_abductive_hypotheses_2.append(g_literal + "imp" + d_literal)
        return pre_abductive_hypotheses_2



    def get_hintikka_sets(gamma : list) -> list:
        hintikka_set = []
        hintikka_set. append[gamma[:]] #TO_DO: spradź, czy dodaje elementy listy czy całą listę

        return hintikka_set

    def get_dual_hintikka_sets(gamma : list) -> list:
        dual_hintikka_set = []
        return dual_hintikka_set

    
    def make_consistent(hintikka_sets: list[list,...]) -> list:
        #TO_DO: sprawdź, czy trzeba sprawdzać też te elementy, które są domyślnie z gammy lub delty. Może wystarczy sprawdzić tylko literały?
        #TO_DO: obecny algorytm jest niezbyt sprytny - brute force + dość długi skomlikowany kod
        consistent_sets = []
        elem1_with_neg = False
        inconsistent = False
        for set in hintikka_sets: 
            if set == inconsistent:
                continue
                inconsistent = False    
            else:
                for elem1 in set:
                    if type(elem1) != str:
                        continue
                    else:
                        if "neg" in elem1:
                            elem1_with_neg = True
                        else:
                            elem1_with_neg = False
                        for elem2 in set:
                            if type(elem2) != str:
                                continue
                            else:
                                if elem1_with_neg:
                                    if elem1 == "neg" + elem2:
                                        inconsistent = True
                                else:
                                    if "neg" + elem1 == elem2:
                                        inconsistent = True
            consistent_sets.append(set)
                        
        return consistent_sets




    def consistency_restrict_1(hintikka_sets : list, l_neg : str) -> list:
        l = _negate_formula(l_neg)
        for set in hintikka_sets:
            if l in set:
                hintikka_sets.remove(set)
        return hintikka_sets

    def consistency_restrict_2(hintikka_sets : list, l : str, k : str) -> list:
        k_neg = _negate_formula(k)
        for set in hintikka_sets:
            if l in set and k_neg in set:
                hintikka_sets.remove(set)
        return hintikka_sets

    def significance_restrict_1(dual_hintikka_sets : list, l_neg : str) -> list:
        for set in dual_hintikka_sets:
            if l_neg in set:
                dual_hintikka_sets.remove(set)
        return dual_hintikka_sets

    def significance_restrict_2(dual_hintikka_sets : list,  l : str, k : str) -> list:
        l_neg = _negate_formula(l)
        for set in hintikka_sets:
            if l_neg in set and k in set:
                hintikka_sets.remove(set)
        return dual_hintikka_sets



    def _negate_formula(form : Union[str, list]) -> str:
        if type(form) == str:
            #add "neg" prefix to literal
            if "neg" in form:
                #prevent double negation like "negneg"
                form = form.replace("neg","")
            else:
                form = "neg" + form
        elif type(form) == list:
            #nest "form" in a list with "neg" as a first element
            form = ["neg",form]
        else:
            raise  TypeError ("<Only strings and lists are allowed>")
        return form
        


string = "p ^ q, q v (r ^ s) |- a -> b"
#print(AQAS_Solver.convert_string(string))
