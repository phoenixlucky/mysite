from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

# Create your views here.
from blog.froms import EmailPostForm
from blog.models import Post


def post_list(request):
    object_list=Post.published.all()
    paginator=Paginator(object_list,3)
    page=request.GET.get('page')
    try:
        posts=paginator.page(page)
    except PageNotAnInteger:
        posts=paginator.page(1)
    except EmptyPage:
        posts=paginator.page(paginator.num_pages)
    return render(request,'blog/post/list.html',{'posts':posts,'page':page})

def post_detail(request,year,month,day,post):
    print(day)
    post=get_object_or_404(Post,slug=post,status='published',publish__year=year,publish__month=month,publish__day=day)
    return render(request,'blog/post/detail.html',{'posts':post})


class PostListView(ListView):
    queryset=Post.published.all()
    context_object_name='posts'
    paginate_by=3
    template_name='blog/post/list.html'

def post_share(request,post_id):
    post=get_object_or_404(Post,id=post_id,status='published')
    if request.method=='POST':
        form=EmailPostForm(request.POST)
        if form.is_valid():
            cd=form.cleaned_data
    else:
        form=EmailPostForm()
    return render(request,'blog/post/share.html',{'post':post,'form':form})