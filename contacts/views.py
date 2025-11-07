from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, get_user_model
from django.db.utils import OperationalError, ProgrammingError
from django.db import connection
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render, get_object_or_404
from .models import Category, Contact, ContactEmail, ContactPhone 
from django.db.models import Q
# Create your views here.

@login_required
def frontpage(request):
    # Safely detect migration state and avoid querying missing columns/tables
    try:
        table_names = connection.introspection.table_names()
    except Exception:
        table_names = []

    if 'contacts_contact' not in table_names:
        contacts = []
    else:
        # Check for owner_id column existence
        try:
            columns = [c.name for c in connection.introspection.get_table_description(connection.cursor(), 'contacts_contact')]
        except Exception:
            columns = []

        has_owner_col = 'owner_id' in columns
        has_shared_table = 'contacts_contact_shared_with' in table_names

        if not has_owner_col:
            contacts = []
        else:
            base_qs = Contact.objects.all().prefetch_related('emails', 'phones')
            if has_shared_table:
                contacts = base_qs.filter(Q(owner=request.user) | Q(shared_with=request.user)).distinct()
            else:
                contacts = base_qs.filter(owner=request.user)

    query = request.GET.get('query', '').strip()
    if query:
        contacts = contacts.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone_number__icontains=query)
            | Q(address__icontains=query)
            | Q(catagory__title__icontains=query)
            | Q(emails__email__icontains=query)
            | Q(phones__phone_number__icontains=query)
        ).distinct()

    return render(request, "core/frontpage.html",{'contacts':contacts})
@login_required
def add_contact(request):
    if request.method == "POST":
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        address=request.POST.get("address")
        category_id=request.POST.get("category")
        emails=[value.strip() for value in request.POST.getlist("emails") if value.strip()]
        phone_numbers=[value.strip() for value in request.POST.getlist("phone_numbers") if value.strip()]

        # Validate that category is selected
        if not category_id or not category_id.strip():
            category=Category.objects.all()
            return render(request, "core/add_contact.html", {
                'category':category,
                'error': 'Please select a category.'
            })
        
        # Validate that category exists
        try:
            Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            category=Category.objects.all()
            return render(request, "core/add_contact.html", {
                'category':category,
                'error': 'Invalid category selected.'
            })

        # Prepare kwargs and only set owner if the column exists (migrations may be pending)
        try:
            columns = [c.name for c in connection.introspection.get_table_description(connection.cursor(), 'contacts_contact')]
        except Exception:
            columns = []
        has_owner_col = 'owner_id' in columns

        create_kwargs = {
            'first_name': first_name,
            'last_name': last_name,
            'email': emails[0] if emails else '',
            'phone_number': phone_numbers[0] if phone_numbers else '',
            'address': address,
            'catagory_id': category_id,
        }
        if has_owner_col:
            create_kwargs['owner'] = request.user

        contact = Contact.objects.create(**create_kwargs)

        for email in emails:
            ContactEmail.objects.create(contact=contact, email=email)

        for phone in phone_numbers:
            ContactPhone.objects.create(contact=contact, phone_number=phone)

        return redirect("frontpage")

    category=Category.objects.all()
    return render(request, "core/add_contact.html",{'category':category})
@login_required
def edit_contact(request, pk):
    contact = get_object_or_404(Contact.objects.prefetch_related('emails', 'phones'), pk=pk)
    if contact.owner_id != request.user.id:
        return redirect('frontpage')
    if request.method == "POST":
        category_id=request.POST.get("category")
        emails=[value.strip() for value in request.POST.getlist("emails") if value.strip()]
        phone_numbers=[value.strip() for value in request.POST.getlist("phone_numbers") if value.strip()]
        
        # Validate that category is selected
        if not category_id or not category_id.strip():
            category=Category.objects.all()
            return render(request, "core/edit_contact.html", {
                'contact': contact,
                'category':category,
                'error': 'Please select a category.'
            })
        
        # Validate that category exists
        try:
            Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            category=Category.objects.all()
            return render(request, "core/edit_contact.html", {
                'contact': contact,
                'category':category,
                'error': 'Invalid category selected.'
            })
        
        contact.catagory_id = category_id
        contact.first_name = request.POST.get("first_name")
        contact.last_name = request.POST.get("last_name")
        contact.address = request.POST.get("address")
        contact.email = emails[0] if emails else ''
        contact.phone_number = phone_numbers[0] if phone_numbers else ''
        contact.save()

        ContactEmail.objects.filter(contact=contact).delete()
        ContactPhone.objects.filter(contact=contact).delete()

        for email in emails:
            ContactEmail.objects.create(contact=contact, email=email)

        for phone in phone_numbers:
            ContactPhone.objects.create(contact=contact, phone_number=phone)

        return redirect("frontpage")
    
    category=Category.objects.all()
    return render(request, "core/edit_contact.html", {
        'contact': contact,
        'category': category
    })

@login_required
def delete_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if contact.owner_id != request.user.id:
        return redirect('frontpage')
    contact.delete()
    return redirect("frontpage")


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("frontpage")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


@login_required
def share_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if contact.owner_id != request.user.id:
        return redirect('frontpage')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        if username:
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
                if user != request.user:
                    try:
                        contact.shared_with.add(user)
                    except (OperationalError, ProgrammingError):
                        # Migrations not applied yet; ignore silently
                        pass
            except User.DoesNotExist:
                pass
    return redirect('edit_contact', pk=pk)


@login_required
def unshare_contact(request, pk, user_id):
    contact = get_object_or_404(Contact, pk=pk)
    if contact.owner_id != request.user.id:
        return redirect('frontpage')
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
        try:
            contact.shared_with.remove(user)
        except (OperationalError, ProgrammingError):
            pass
    except User.DoesNotExist:
        pass
    return redirect('edit_contact', pk=pk)