from random import choice,randint
result_types = [['Success','Failure'],['Advantage','Threat'],'Triumph','Despair','Light','Dark']
def plural(type_):
    if type_ == 'Success':
        return 'Successes'
    else:
        return f'{type_}s'
class result:
    def __init__(self,name,image):
        self.name = name
        self.image = image
class die:
    def __init__(self,name,sides):
        self.name = name
        self.sides = sides

def roll_sw_dice(number,types):
    results_raw = []
    for i in range(len(number)):
        for j in range(number[i]):
            if j<number[i]:
                results_raw.append(choice(types[i].sides))
            else:
                continue
    inter_results = []
    for res in results_raw:
        multiplier=int(res[0])
        for side in res[1]:
            inter_results.append((f'{side.name} '*multiplier).strip())
    results = []
    for i in range(len(inter_results)):
        if ' ' in inter_results[i]:
            split = inter_results[i].split(' ')
            for j in split:
                results.append(j)
        else:
            results.append(inter_results[i])
    outcome = []
    for type_ in result_types:
        if isinstance(type_,list) :
            total = 0
            for die in type_:
                count = results.count(die)
                if die in ['Success','Advantage']:
                    total += count
                elif die in ['Failure','Threat']:
                    total += -count
            total += results.count('Triumph')
            total += -results.count('Despair')
            if total == 1:
                outcome.append(f'{total} {type_[0]}, ')
            elif total > 1:
                outcome.append(f'{total} {plural(type_[0])}, ')
            elif total == -1:
                outcome.append(f'{-total} {type_[1]}, ')
            elif total < -1:
                outcome.append(f'{-total} {plural(type_[1])}, ')
            elif total == 0:
                continue
        else:
            count = results.count(type_)
            if count==0:
                continue
            elif count==1:
                outcome.append(f'{count} {type_}, ')
            else:
                outcome.append(f'{count} {plural(type_)}, ')
    if len(outcome)==1:
        return outcome[0].replace(', ','')
    elif len(outcome)==2:
        final_outcome = []
        final_outcome.append(outcome[0].replace(',',''))
        last_item = outcome[1].replace(', ','')
        final_outcome.append(f'and {last_item}')
        final_outcome = ''.join(final_outcome)
        return final_outcome
    else:
        final_outcome = []
        for i in range(len(outcome)):
            if i < len(outcome)-1:
                final_outcome.append(outcome[i])
            else:
                last_item = outcome[i].replace(', ','')
                final_outcome.append(f'and {last_item}')
        final_outcome = ''.join(final_outcome)
        return final_outcome

success = result('Success',r'figs\success.png')
advantage = result('Advantage',r'figs\advantage.png')
failure = result('Failure',r'figs\failure.png')
triumph = result('Triumph',r'figs\triumph.png')
threat = result('Threat',r'figs\threat.png')
despair = result('Despair',r'figs\despair.png')
light = result('Light',r'figs\light_side.png')
dark = result('Dark',r'figs\dark_side.png')
blank = result('Blank',r'figs\blank.png')

force = die('Force',[(2, [light]),(2, [light]),(2, [light]),(1, [light]),(1, [light]),(2,[dark]),(1,[dark]),(1,[dark]),(1,[dark]),(1,[dark]),(1,[dark]),(1,[dark])])
ability = die('Ability',[(1,[success,advantage]),(1, [success]),(1, [success]),(2,[success]),(1,[advantage]),(1,[advantage]),(2,[advantage]),(0, [blank])])
proficiency = die('Proficiency',[(1,[success]),(1,[success]),(2,[success]),(2,[success]),(2,[advantage]),(2,[advantage]),(1,[advantage]),(1,[triumph]),(1,[blank]),(1,[advantage,success]),(1,[advantage,success]),(1,[advantage,success])])
boost = die('Boost',[(1,[blank]),(1,[blank]),(1,[advantage]),(1,[success]),(2,[advantage]),(1,[success,advantage])])
difficulty = die('Difficulty',[(1,[threat]),(1,[threat]),(1,[threat]),(2,[threat]),(1,[blank]),(1,[failure]),(2,[failure]),(1,[failure,threat])])
challenge = die('Challenge',[(1,[threat]),(1,[threat]),(2,[threat]),(2,[threat]),(2,[failure]),(2,[failure]),(1,[failure]),(1,[failure]),(1,[despair]),(1,[blank]),(1,[failure,threat]),(1,[failure,threat])])
setback = die('Setback',[(1,[failure]),(1,[failure]),(1,[threat]),(1,[threat]),(1,[blank]),(1,[blank])])

success_thresholds = {
    'fumble': lambda x: (94 if x<50 else 99,100),
    'failure':lambda x: (x,94 if x<50 else 100),
    'success':lambda x: (int(x/2),x),
    'hard success':lambda x: (int(x/5),int(x/2)),
    'critical success':lambda x: (0,1)
    }

def roll(val):
    die_result = randint(0,100)
    calc_thresh = {key:success_thresholds[key](val) for key in success_thresholds}
    for key in calc_thresh:
        if calc_thresh[key][0]<die_result<=calc_thresh[key][1]:
            result_desc = key
    return die_result,result_desc