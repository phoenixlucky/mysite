from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

# Create your views here.
from taggit.models import Tag

from blog.froms import EmailPostForm, CommentForm
from blog.models import Post

def post_list(request,tag_slug=None):
    object_list=Post.published.all()
    tag=None

    if tag_slug:
        tag=get_object_or_404(Tag,slug=tag_slug)
        object_list=object_list.filter(tags__in=[tag])
    paginator=Paginator(object_list,3)
    page=request.GET.get('page')
    try:
        posts=paginator.page(page)
    except PageNotAnInteger:
        posts=paginator.page(1)
    except EmptyPage:
        posts=paginator.page(paginator.num_pages)
    return render(request,'blog/post/list.html',{'posts':posts,'page':page,'tag':tag})

def post_detail(request,year,month,day,post):
    post=get_object_or_404(Post,slug=post,status='published',publish__year=year,publish__month=month,publish__day=day)
    #评论栏活动列表
    comments=post.comments.filter(active=True)
    new_comment=None
    comment_form=None
    if request.method=='POST':
        comment_form=CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment=comment_form.save(commit=False)
            new_comment.post=post
            new_comment.save()
        else:
            comment_form=CommentForm()
    #相似文章
    post_tags_ids=post.tags.values_list('id',flat=True)
    similar_posts=Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts=similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
    return render(request,'blog/post/detail.html',{'posts':post,'comments':comments,'new_comment':new_comment,
                                                   'comment_form':comment_form,'similar_posts':similar_posts})


class PostListView(ListView):
    queryset=Post.published.all()
    context_object_name='posts'
    paginate_by=3
    template_name='blog/post/list.html'

def post_share(request,post_id):
    post=get_object_or_404(Post,id=post_id,status='published')
    sent=False

    if request.method=='POST':
        form=EmailPostForm(request.POST)
        if form.is_valid():
            cd=form.cleaned_data
            post_url=request.build_absolute_uri(post.get_absolute_url())
            subject='{} ({}) recommends you reading "{}"'.format(cd['name'],cd['email'],post.title)
            message='Read "{}" at {}\n\n{}\'s comments:{}'.format(post.title,post_url,cd['name'],cd['comments'])
            send_mail(subject,message,cd['email'],[cd['to']])
            sent=True
    else:
        form=EmailPostForm()
    return render(request,'blog/post/share.html',{'posts':post,'form':form,'sent':sent})