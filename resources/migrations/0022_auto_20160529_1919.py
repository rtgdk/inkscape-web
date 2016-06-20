# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def unique_lc_tags(apps, schema_editor):
    """Make tags lowercase and re-link the lowercase version to their respective resources"""
    Tag = apps.get_model("resources", "Tag")
    
    # pks of all tags that are no longer needed
    tags2delete = []
    
    for tag in Tag.objects.all():
        # only look at a tag if it needs to be changed and
        # hasn't been looked at yet. 
        # Condition looks like overkill... but also catches duplicate lowercase tags
        if tag.pk not in tags2delete and \
          (tag.name != tag.name.lower() or \
           (tag.name == tag.name.lower() and Tag.objects.filter(name=tag.name).count() > 1 and \
             Tag.objects.filter(name__iexact=tag.name).count() == Tag.objects.filter(name=tag.name).count())):
            
            old_tags = Tag.objects.filter(name__iexact=tag.name)
            
            old_tag_pks = [tag.pk for tag in old_tags]
            
            # keep old tag categories (at least one of them)
            old_tag_categories = set([tag.category for tag in old_tags])
            if len(old_tag_categories) > 0:
               old_tag_category = old_tag_categories.pop()
            else:
               old_tag_category = None
            
            tags2delete += old_tag_pks
            new_tag = Tag.objects.create(name=tag.name.lower(), category=old_tag_category)

            # For all the ManyToMany Fields that point to the Tag model
            for m2m_field in Tag._meta.get_all_related_many_to_many_objects():
                # Get the connecting model that connects tables for many to many fields
                through_model = m2m_field.through
                tag_field = None
                related_field = None

                # For all the fields in the 'through' model.
                for field in through_model._meta.fields:

                    # Select the one that points back to the Tag model
                    if field.rel and field.rel.to is Tag:
                        tag_field_name = field.name

                    # Select the one that points to the Resource model (or any other model)
                    if field.rel and field.rel.to is m2m_field.related_model:
                        related_field_name = field.name

                if not tag_field_name or not related_field_name:
                    # Error should never happen
                    continue
                
                # all pks of objects that are tagged with a variation of the current tag
                objects_tagged_w_current_tag = []
                
                # Look through all connections and update or remove them
                for connection in through_model.objects.all():
                    # check if the connection refers to any of our current tag variants
                    if getattr(connection, tag_field_name).pk in old_tag_pks:
                        connection_rel_obj_pk = getattr(connection, related_field_name).pk
                        # check if the connection for this resource already has been updated
                        if connection_rel_obj_pk not in objects_tagged_w_current_tag: 
                            # no variable variable names...
                            to_new_tag = {tag_field_name: new_tag.pk}
                            # Inefficient, but easy workaround for 
                            # not being able to update the object directly
                            through_model.objects.filter(pk=connection.pk).update(**to_new_tag)
                            objects_tagged_w_current_tag.append(connection_rel_obj_pk)
                        else:
                            # the resource already has that tag
                            connection.delete()

    # finally, remove all superfluous (uppercase and lowercase) tags
    for tag in Tag.objects.all():
        if tag.pk in tags2delete:
            tag.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0021_auto_20160527_0115'),
    ]

    operations = [
        migrations.RunPython(unique_lc_tags),
    ]
        
