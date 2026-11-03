from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q, ProtectedError
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from noticias.models import Categoria, Noticia
from cine.models import Genero, Pelicula
from .models import Funcion, Reserva
from django.utils import timezone
from django.db.models import Sum

from .forms import UsuarioForm, PerfilForm

ENTIDADES = {
 'categorias': (Categoria,['nombre','descripcion'],['nombre','descripcion']),
 'noticias': (Noticia,['titulo','categoria','fecha','resumen','contenido','destacado','imagen'],['titulo','resumen','categoria__nombre']),
 'generos': (Genero,['nombre','descripcion'],['nombre','descripcion']),
 'peliculas': (Pelicula,['titulo','director','genero','anio','calificacion','sinopsis','estreno','imagen'],['titulo','director','genero__nombre']),
 'funciones': (Funcion,['pelicula','fecha','cupos'],['pelicula__titulo']),
}

def permiso(user, model, accion):
    return user.has_perm(f'{model._meta.app_label}.{accion}_{model._meta.model_name}')

def exigir(user, model, accion):
    if not permiso(user, model, accion):
        raise PermissionDenied

def estilo(form):
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-check-input' if isinstance(field.widget, forms.CheckboxInput) else 'form-control'
        if isinstance(field, forms.DateTimeField):
            field.widget = forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type':'datetime-local','class':'form-control'})
        elif isinstance(field, forms.DateField):
            field.widget = forms.DateInput(format='%Y-%m-%d', attrs={'type':'date','class':'form-control'})
    return form

@login_required
def inicio(request):
    grupo = request.user.groups.filter(name__in=['Administrador','Supervisor','Administrativo']).first()
    perfil = 'Administrador' if request.user.is_superuser else (grupo.name if grupo else 'Sin perfil')
    modulos = []
    for slug,(model,fields,search) in ENTIDADES.items():
        if permiso(request.user,model,'view'):
            modulos.append((slug.capitalize(), reverse('gestion:lista', args=[slug]), model.objects.count()))
    if permiso(request.user,Reserva,'view'):
        modulos.append(('Reservas',reverse('gestion:reservas'),Reserva.objects.count()))
    reservas = Reserva.objects.select_related('funcion__pelicula','usuario')
    if perfil == 'Administrativo':
        reservas = reservas.filter(usuario=request.user)
    contexto = {'perfil':perfil,'modulos':modulos,
        'reservas_recientes':reservas[:5] if permiso(request.user,Reserva,'view') else [],
        'funciones_proximas':Funcion.objects.select_related('pelicula').filter(fecha__gt=timezone.now())[:5] if permiso(request.user,Funcion,'view') else [],
        'total_usuarios':User.objects.count() if request.user.has_perm('auth.view_user') else None}
    return render(request,'gestion/dashboard.html',contexto)

@login_required
def entidad(request, slug, pk=None, accion='view'):
    if slug not in ENTIDADES:
        from django.http import Http404
        raise Http404
    model, fields, search = ENTIDADES[slug]
    exigir(request.user,model,accion)
    url = reverse('gestion:lista',args=[slug])
    obj = get_object_or_404(model,pk=pk) if pk else None
    if accion == 'view':
        q = request.GET.get('q','').strip()
        qs = model.objects.all()
        if q:
            filtro = Q()
            for field in search:
                filtro |= Q(**{field+'__icontains':q})
            qs = qs.filter(filtro)
        from django.core.paginator import Paginator
        page = Paginator(qs,10).get_page(request.GET.get('page'))
        return render(request,'gestion/lista.html',{'titulo':slug.capitalize(),'slug':slug,'page_obj':page,'q':q,
            'puede_agregar':permiso(request.user,model,'add'),'puede_modificar':permiso(request.user,model,'change'),
            'puede_eliminar':permiso(request.user,model,'delete')})
    if accion == 'delete':
        if request.method == 'POST':
            try:
                obj.delete()
                messages.success(request,'Registro eliminado.')
                return redirect(url)
            except ProtectedError:
                messages.error(request,'No se puede eliminar: existen registros relacionados.')
        return render(request,'gestion/eliminar.html',{'object':obj,'volver':url})
    Form = forms.modelform_factory(model, fields=fields)
    form = Form(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        if model is Pelicula and not 0 <= form.cleaned_data['calificacion'] <= 10:
            form.add_error('calificacion','La calificación debe estar entre 0 y 10.')
        elif model is Pelicula and not 1888 <= form.cleaned_data['anio'] <= timezone.now().year+5:
            form.add_error('anio','Ingresa un año entre 1888 y los próximos cinco años.')
        elif model is Funcion and obj and (obj.reservas.filter(cancelada=False).aggregate(n=Sum('cantidad'))['n'] or 0) > form.cleaned_data['cupos']:
            form.add_error('cupos','No puede ser menor que las entradas ya reservadas.')
        else:
            form.save()
            messages.success(request,'Registro guardado.')
            return redirect(url)
    return render(request,'gestion/form.html',{'form':estilo(form),'titulo':('Modificar ' if obj else 'Crear ')+slug,'volver':url})


@login_required
@permission_required('gestion.view_reserva',raise_exception=True)
def reservas(request):
    qs=Reserva.objects.select_related('funcion__pelicula','usuario')
    return render(request,'gestion/reservas.html',{'reservas':qs})

@login_required
@permission_required('gestion.add_reserva',raise_exception=True)
def reservar(request):
    class ReservaForm(forms.ModelForm):
        class Meta:
            model=Reserva
            fields=['funcion','cantidad']
    form=ReservaForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            funcion=Funcion.objects.select_for_update().get(pk=form.cleaned_data['funcion'].pk)
            ocupados=funcion.reservas.filter(cancelada=False).aggregate(n=Sum('cantidad'))['n'] or 0
            if funcion.fecha <= timezone.now():
                form.add_error('funcion','La función ya comenzó.')
            elif form.cleaned_data['cantidad'] > funcion.cupos-ocupados:
                form.add_error('cantidad',f'Solo quedan {funcion.cupos-ocupados} cupos.')
            else:
                reserva=form.save(commit=False)
                reserva.usuario=request.user
                reserva.save()
                messages.success(request,'Reserva registrada correctamente.')
                return redirect('gestion:reservas')
    return render(request,'gestion/form.html',{'form':estilo(form),'titulo':'Reservar entradas','volver':reverse('gestion:reservas')})

@login_required
@permission_required('gestion.change_reserva',raise_exception=True)
def cancelar(request,pk):
    obj=get_object_or_404(Reserva,pk=pk)
    if request.method=='POST':
        with transaction.atomic():
            Funcion.objects.select_for_update().get(pk=obj.funcion_id)
            obj.cancelada=True
            obj.save(update_fields=['cancelada'])
        return redirect('gestion:reservas')
    return render(request,'gestion/cancelar.html',{'object':obj})
@login_required
@permission_required('auth.view_user',raise_exception=True)
def usuarios(request):
    return render(request,'gestion/usuarios.html',{'usuarios':User.objects.prefetch_related('groups').order_by('username')})

@login_required
def usuario_form(request,pk=None):
    exigir(request.user,User,'change' if pk else 'add')
    user=get_object_or_404(User,pk=pk) if pk else None
    if user and (user.is_superuser or user.pk==request.user.pk):
        raise PermissionDenied('No puedes modificar tu propia cuenta ni un superusuario desde este formulario.')
    if user:
        form=PerfilForm(request.POST or None,instance=user,initial={'grupo':user.groups.first()})
    else:
        form=UsuarioForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        form.save()
        return redirect('gestion:usuarios')
    return render(request,'gestion/form.html',{'form':estilo(form),'titulo':'Usuario y perfil','volver':reverse('gestion:usuarios')})
