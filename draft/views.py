import datetime
import math
import random
from django import forms
from django.forms import IntegerField
from django.shortcuts import get_object_or_404, redirect, render

from .forms import GroupForm, PlayerSelectForm
from .models import Group, People, Team, Player


TIMEOUT = datetime.timedelta(seconds=300)


# Create your views here.

def index(request):
    return render(request, "draft/index.html", {
        'people': People.objects.all(),
        'groups': Group.objects.all()
    })


def new_draft(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            # create new Group instance and save it
            group = Group.objects.create(name=form.cleaned_data['group_name'])

            # Create array to store the draft order
            draft_order = []

            # Create a new People instance for each member and save it
            for i in range(1, 11):
                member_name = form.cleaned_data.get(f"member_{i}")
                if member_name:
                    # Create member
                    People.objects.create(name=member_name, group_id=group)

                    # Add member ID to draft_order
                    member_id = People.objects.get(name=member_name).id
                    draft_order.append(member_id)
                    print(f'draft order{draft_order}')

            # Randomize draft order
            random.shuffle(draft_order)

            # Set snake draft by adding reverse order
            draft_order = draft_order + draft_order[::-1]

            # Add draft order to list
            group.draft_order = draft_order
            group.save()

            # Redirect to a success page
            return redirect('group', group_id=group.id)
    context = {
        'form': GroupForm(),
        'groups': Group.objects.all()
    }
    return render(request, "draft/new_draft.html", context)


def group(request, group_id):

    group = Group.objects.get(id=group_id)
    for person in People.objects.filter(group_id=group_id):
        print(person.player_count)

    draft_order = []

    for p in group.draft_order:
        memb = People.objects.get(id=p)
        draft_order.append(memb)

    # get first half of draft array
    mid_index = len(draft_order) // 2
    first_half = draft_order[:mid_index]

    context = {
        'group': group,
        'draft_order': first_half,
        'groups': Group.objects.all()
    }

    return render(request, 'draft/group.html', context)


def draft(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    people = People.objects.filter(group_id=group_id)

    drafted_players = []
    for person in people:
        for player in person.players.all():
            drafted_players.append(player)

    remaining_players = Player.objects.exclude(
        id__in=[p.id for p in drafted_players])

    # Keep track of how many players have been added
    player_counter = 0

    for person in people:
        player_counter += person.player_count

    if player_counter >= group.round_length:
        player_counter = player_counter % group.round_length

    index_val = group.draft_order[player_counter]

    current_member = People.objects.get(id=index_val)

    # Calculate what round the draft is on
    draft_round = 0
    if len(drafted_players) / int(len(group.draft_order)/2) >= 1:
        draft_round = len(drafted_players) / int(len(group.draft_order)/2)

    draft_round += 1

    if request.method == 'POST':
        # Handle form submission
        form = PlayerSelectForm(
            group_id=group_id, remaining_players=remaining_players, data=request.POST)

        if form.is_valid():

            # Add the chosen player to the list
            player_id = form.cleaned_data['player'].id
            current_member.players.add(player_id)

            # Redirect to the same page to avoid form resubmission on refresh
            return redirect('draft', group_id=group_id)

    select = PlayerSelectForm(
        remaining_players=remaining_players,
        group_id=group_id,
        data={'group_id': group_id}
    )

    draft_order = []

    for p in group.draft_order:
        memb = People.objects.get(id=p)
        draft_order.append(memb)

    # get first half of draft array
    mid_index = len(draft_order) // 2
    first_half = draft_order[:mid_index]

    context = {
        'group': group,
        'people': people,
        'draft_order': first_half,
        'select': select,
        'remaining_player': remaining_players,
        'current_turn': current_member,
        'round': math.floor(draft_round),
        'groups': Group.objects.all()
    }
    return render(request, 'draft/draft.html', context)
