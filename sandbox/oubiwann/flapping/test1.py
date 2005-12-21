'''
Rules and defintions for this example
-------------------------------------
count = the number of times a service has been in the current state;
gets reset upon state transition

cutoff = 3; after 3 emails about one service in warn, error, or
failed, we get no more emails until the state changes

flap = a behavior of transitioning between states, spending less
counts in each message-generating state than the cutoff amount

flap span = 10; if the number of service polls (checks) to check
for flaps (i.e., how far back in the history to look for flap
occurrences)

flap cutoff = 5; after a service flaps 5 times, we no longer get
an email until it reaches steady state again

steady state cutoff = 10; after being tagged as a flapping service,
a service will no longer be considered flapping once it has stayed
in a given state for a count of 10

msg count = the number of times an email has been sent as a result
of service change; reset when going from service flap to steady-state

message-generating state transitions = for this example, we will
just consider the following:

ok -> warn
ok -> error
ok -> failed
warn -> ok
error -> ok
failed -> ok

The coding problem: If your flap cutoff can be an arbitrary integer,
then the record of transitions you need to keep in-memory could be
arbitrarily large. This is obviously poor design. How do we encode
an arbitrarily long chain of state transitions in a small memory
space? To advance an answer to that, what is the least amount of
necessary information to encode flapping?
'''
import time
from random import choice

states = ['ok', 'warn', 'error', 'failed']
pattern = ['ok','ok','ok','ok','ok','ok','ok','ok','ok',
'ok','warn','ok','warn','ok','warn','ok','warn','ok','warn',
'ok','warn','ok','warn','ok','warn','ok','warn','ok','warn',
'ok','ok','ok','ok','ok','ok','ok','ok','ok','ok','ok','ok',
'ok','ok','ok','ok','ok','ok','ok','ok','ok','ok','ok','ok',
]
sendmsg = ['ok:warn', 'ok:error', 'ok:failed', 'warn:ok', 'error:ok', 'failed:ok']

transitions = []
msgs = []
this_state = 'ok'
last_state = 'ok'
count = 0
flapcount = 0
sscount = 0
msgcount = 0
flapped = False

cutoff = 3
flapcutoff = 5
flapspan = 10
sscutoff = 10

def doMsg(this_transition):
    global count
    global sendmsg
    global flapped
    global msgcount
    if (this_transition in sendmsg 
        and (count <= cutoff) and not flapped):
        msgcount += 1
        return True
    return False

def transit():
    global pattern
    global last_state
    global this_state
    global transitions
    global msgs
    global count
    global flapcount
    global sscount
    global msgcount
    global flapped
    last_state = this_state
    #this_state = choice(states)
    this_state = pattern.pop(0)
    if this_state == last_state:
        count += 1
    else:
        count = 0
    # check to see if the service is out of the doghouse
    if count >= sscutoff and flapped == True:
        print "(no longer flapped)"
        flapped = False
    transition = '%s:%s' % (last_state,  this_state)
    transitions.insert(0, transition)
    is_msg = doMsg(transition)
    msgs.insert(0, is_msg)
    # the minium number of msg counts needed to consider a service
    # as "flapped" is flapcutoff
    if len(msgs) >= flapcutoff:
	# we're only interested in keeping a history of length
	# flapspan
        if len(msgs) > flapspan:
            msgs.pop()
	# for every msg sent, there will be a True/1, and for one
	# not sent, a False/0 summing these will give us the number
	# of msgs sent in the flapspan
        total = sum(msgs)
        print "(total: %s, flapcutoff: %s)" % (total, flapcutoff)
        if total >= flapcutoff:
            flapped = True
            flapcount += 1

    # report
    print "Last status: %s" % last_state
    print "This status: %s" % this_state
    print "This transition: %s" % transition
    print "Count: %s" % count
    print "Message sent? %s" % is_msg
    print msgs
    print "Messages send in flap span: %s" % sum(msgs)
    print "Is email cut off? %s" % (count > cutoff)
    print "Is service flapped? %s" % flapped
    print
    time.sleep(1)

pat_len = len(pattern)
for i in range(0,pat_len):
    print pattern
    transit()
