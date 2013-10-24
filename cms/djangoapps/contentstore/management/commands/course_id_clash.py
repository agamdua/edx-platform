"""
Script for finding all courses whose org/name pairs == other courses when ignoring case
"""
from django.core.management.base import BaseCommand
from xmodule.modulestore.django import modulestore


#
# To run from command line: rake cms:delete_course LOC=MITx/111/Foo1
#
class Command(BaseCommand):
    help = 'List all courses ids which may collide when ignoring case'

    def handle(self, *args, **options):
        mstore = modulestore()
        if hasattr(mstore, 'collection'):
            results = mstore.collection.map_reduce(
                '''
                function () {
                    emit(this._id.org.toLowerCase()+this._id.course.toLowerCase(), {target: this._id});
                }
                ''',
                '''
                function (idpair, matches) {
                    var result = {target: []};
                    matches.forEach(function (match) {
                        result.target.push(match.target);
                    });
                    return result;
                }
                ''',
                {'inline': True},
                query={'_id.category': 'course'},
                finalize='''
                function(key, reduced) {
                    if (Array.isArray(reduced.target)) {
                        return reduced;
                    }
                    else {return null;}
                    }
                '''
            )
            results = results.get('results')
            for entry in results:
                if entry.get('value') is not None:
                    print '{:-^40}'.format(entry.get('_id'))
                    for course_id in entry.get('value').get('target'):
                        print '   {}/{}/{}'.format(course_id.get('org'), course_id.get('course'), course_id.get('name'))

