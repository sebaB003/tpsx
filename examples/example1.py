from tpsx import *

tpsx = TopicsExtractor(ITALIAN)
tpsx.train('animali', 'coda pelliccia artiglio zampa zoccolo criniera proboscide muso cane gatto giraffa elefante lupo orso serpente'.split(' '))
tpsx.train('felini', 'gatto lince leone baffi')
tpsx.train('volatili', 'ali piume rapaci acquila uccelo pettirosso volare'.split(' '))
tpsx.train('pesci', 'branchie pinne squame nemo'.split(' '))

# Define topic relations
# topic1 topic2 coexists bidirectional relation
tpsx.add_related_topic('felini', 'animali', True, True)
tpsx.add_related_topic('animali', 'pesci', True, True)
tpsx.add_related_topic(['volatili'], 'pesci', False, True)
tpsx.add_related_topic('animali', ['volatili', 'pesci', 'felini'], True, True)


for r in tpsx.related_topics:
    print(r)

# Predict a text
results = tpsx.predict(['I gatti mangiano i pesci (non nemo) anche quelli che volano'], True)

# Display results
for result in results:
    results[result].show_data(True)
